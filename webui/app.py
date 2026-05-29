import os
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.utils
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import warnings
import datetime
warnings.filterwarnings('ignore')

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from model import Kronos, KronosTokenizer, KronosPredictor
    MODEL_AVAILABLE = True
except Exception as _model_err:
    import traceback as _tb
    MODEL_AVAILABLE = False
    _err_msg = _tb.format_exc()
    print(f"Warning: Kronos model import failed:\n{_err_msg}")
    # 写入日志文件方便排查
    try:
        import os as _os
        _log = _os.path.join(
            _os.environ.get('APPDATA', _os.path.expanduser('~')),
            'KronosWebUI', 'model_import_error.log'
        )
        _os.makedirs(_os.path.dirname(_log), exist_ok=True)
        with open(_log, 'w', encoding='utf-8') as _f:
            _f.write(_err_msg)
    except Exception:
        pass

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except Exception:
    AKSHARE_AVAILABLE = False
    print("Warning: AKShare unavailable")

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except Exception:
    TUSHARE_AVAILABLE = False
    print("Warning: Tushare unavailable")

# Token 持久化存储路径（优先写到 APPDATA 可写目录，打包环境下 __file__ 目录只读）
_TOKEN_FILE = os.path.join(
    os.environ.get('APPDATA', os.path.dirname(os.path.abspath(__file__))),
    'KronosWebUI', '.tushare_token'
)

def _load_tushare_token():
    if os.path.exists(_TOKEN_FILE):
        with open(_TOKEN_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ''

def _save_tushare_token(token):
    with open(_TOKEN_FILE, 'w', encoding='utf-8') as f:
        f.write(token.strip())


# 打包模式下使用 launcher.py 传入的 template 目录，否则用默认值
_template_dir = os.environ.get('KRONOS_TEMPLATE_DIR', None)
app = Flask(__name__, template_folder=_template_dir) if _template_dir else Flask(__name__)
CORS(app)

# Global variables to store models
tokenizer = None
model = None
predictor = None

# Available model configurations
AVAILABLE_MODELS = {
    'kronos-mini': {
        'name': 'Kronos-mini',
        'model_id': 'NeoQuasar/Kronos-mini',
        'tokenizer_id': 'NeoQuasar/Kronos-Tokenizer-2k',
        'context_length': 2048,
        'params': '4.1M',
        'description': '轻量级模型，适合快速预测'
    },
    'kronos-small': {
        'name': 'Kronos-small',
        'model_id': 'NeoQuasar/Kronos-small',
        'tokenizer_id': 'NeoQuasar/Kronos-Tokenizer-base',
        'context_length': 512,
        'params': '24.7M',
        'description': '小型模型，性能与速度均衡'
    },
    'kronos-base': {
        'name': 'Kronos-base',
        'model_id': 'NeoQuasar/Kronos-base',
        'tokenizer_id': 'NeoQuasar/Kronos-Tokenizer-base',
        'context_length': 512,
        'params': '102.3M',
        'description': '基础模型，提供更好的预测质量'
    }
}

def _get_data_dir():
    return os.environ.get('KRONOS_DATA_DIR',
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data'))

def _get_results_dir():
    return os.environ.get('KRONOS_RESULTS_DIR',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prediction_results'))

def load_data_files():
    """Scan data directory and return available data files"""
    data_dir = _get_data_dir()
    data_files = []
    
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith(('.csv', '.feather')):
                file_path = os.path.join(data_dir, file)
                file_size = os.path.getsize(file_path)
                data_files.append({
                    'name': file,
                    'path': file_path,
                    'size': f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
                })
    
    return data_files

def load_data_file(file_path):
    """Load data file"""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.feather'):
            df = pd.read_feather(file_path)
        else:
            return None, "不支持的文件格式"
        
        # Check required columns
        required_cols = ['open', 'high', 'low', 'close']
        if not all(col in df.columns for col in required_cols):
            return None, f"缺少必需列：{required_cols}"
        
        # Process timestamp column
        if 'timestamps' in df.columns:
            df['timestamps'] = pd.to_datetime(df['timestamps'])
        elif 'timestamp' in df.columns:
            df['timestamps'] = pd.to_datetime(df['timestamp'])
        elif 'date' in df.columns:
            # If column name is 'date', rename it to 'timestamps'
            df['timestamps'] = pd.to_datetime(df['date'])
        else:
            # If no timestamp column exists, create one
            df['timestamps'] = pd.date_range(start='2024-01-01', periods=len(df), freq='1H')
        
        # Ensure numeric columns are numeric type
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Process volume column (optional)
        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        # Process amount column (optional, but not used for prediction)
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Remove rows containing NaN values
        df = df.dropna()
        
        return df, None
        
    except Exception as e:
        return None, f"文件加载失败：{str(e)}"

def save_prediction_results(file_path, prediction_type, prediction_results, actual_data, input_data, prediction_params):
    """Save prediction results to file"""
    try:
        # Create prediction results directory
        results_dir = _get_results_dir()
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'prediction_{timestamp}.json'
        filepath = os.path.join(results_dir, filename)
        
        # Prepare data for saving
        save_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'file_path': file_path,
            'prediction_type': prediction_type,
            'prediction_params': prediction_params,
            'input_data_summary': {
                'rows': len(input_data),
                'columns': list(input_data.columns),
                'price_range': {
                    'open': {'min': float(input_data['open'].min()), 'max': float(input_data['open'].max())},
                    'high': {'min': float(input_data['high'].min()), 'max': float(input_data['high'].max())},
                    'low': {'min': float(input_data['low'].min()), 'max': float(input_data['low'].max())},
                    'close': {'min': float(input_data['close'].min()), 'max': float(input_data['close'].max())}
                },
                'last_values': {
                    'open': float(input_data['open'].iloc[-1]),
                    'high': float(input_data['high'].iloc[-1]),
                    'low': float(input_data['low'].iloc[-1]),
                    'close': float(input_data['close'].iloc[-1])
                }
            },
            'prediction_results': prediction_results,
            'actual_data': actual_data,
            'analysis': {}
        }
        
        # If actual data exists, perform comparison analysis
        if actual_data and len(actual_data) > 0:
            # Calculate continuity analysis
            if len(prediction_results) > 0 and len(actual_data) > 0:
                last_pred = prediction_results[0]  # First prediction point
            first_actual = actual_data[0]      # First actual point
                
            save_data['analysis']['continuity'] = {
                    'last_prediction': {
                        'open': last_pred['open'],
                        'high': last_pred['high'],
                        'low': last_pred['low'],
                        'close': last_pred['close']
                    },
                    'first_actual': {
                        'open': first_actual['open'],
                        'high': first_actual['high'],
                        'low': first_actual['low'],
                        'close': first_actual['close']
                    },
                    'gaps': {
                        'open_gap': abs(last_pred['open'] - first_actual['open']),
                        'high_gap': abs(last_pred['high'] - first_actual['high']),
                        'low_gap': abs(last_pred['low'] - first_actual['low']),
                        'close_gap': abs(last_pred['close'] - first_actual['close'])
                    },
                    'gap_percentages': {
                        'open_gap_pct': (abs(last_pred['open'] - first_actual['open']) / first_actual['open']) * 100,
                        'high_gap_pct': (abs(last_pred['high'] - first_actual['high']) / first_actual['high']) * 100,
                        'low_gap_pct': (abs(last_pred['low'] - first_actual['low']) / first_actual['low']) * 100,
                        'close_gap_pct': (abs(last_pred['close'] - first_actual['close']) / first_actual['close']) * 100
                    }
                }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        print(f"Prediction results saved to: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Failed to save prediction results: {e}")
        return None

def create_prediction_chart(df, pred_df, lookback, pred_len, actual_df=None, historical_start_idx=0):
    """Create prediction chart"""
    # Use specified historical data start position, not always from the beginning of df
    if historical_start_idx + lookback + pred_len <= len(df):
        # Display lookback historical points + pred_len prediction points starting from specified position
        historical_df = df.iloc[historical_start_idx:historical_start_idx+lookback]
        prediction_range = range(historical_start_idx+lookback, historical_start_idx+lookback+pred_len)
    else:
        # If data is insufficient, adjust to maximum available range
        available_lookback = min(lookback, len(df) - historical_start_idx)
        available_pred_len = min(pred_len, max(0, len(df) - historical_start_idx - available_lookback))
        historical_df = df.iloc[historical_start_idx:historical_start_idx+available_lookback]
        prediction_range = range(historical_start_idx+available_lookback, historical_start_idx+available_lookback+available_pred_len)
    
    # Create chart
    fig = go.Figure()
    
    # Add historical data (candlestick chart)
    fig.add_trace(go.Candlestick(
        x=historical_df['timestamps'] if 'timestamps' in historical_df.columns else historical_df.index,
        open=historical_df['open'],
        high=historical_df['high'],
        low=historical_df['low'],
        close=historical_df['close'],
        name=f'历史数据（{lookback} 个数据点）',
        increasing_line_color='#26A69A',
        decreasing_line_color='#EF5350'
    ))
    
    # Add prediction data (candlestick chart)
    if pred_df is not None and len(pred_df) > 0:
        # Calculate prediction data timestamps - ensure continuity with historical data
        if 'timestamps' in df.columns and len(historical_df) > 0:
            # Start from the last timestamp of historical data, create prediction timestamps with the same time interval
            last_timestamp = historical_df['timestamps'].iloc[-1]
            time_diff = df['timestamps'].iloc[1] - df['timestamps'].iloc[0] if len(df) > 1 else pd.Timedelta(hours=1)
            
            pred_timestamps = pd.date_range(
                start=last_timestamp + time_diff,
                periods=len(pred_df),
                freq=time_diff
            )
        else:
            # If no timestamps, use index
            pred_timestamps = range(len(historical_df), len(historical_df) + len(pred_df))
        
        fig.add_trace(go.Candlestick(
            x=pred_timestamps,
            open=pred_df['open'],
            high=pred_df['high'],
            low=pred_df['low'],
            close=pred_df['close'],
            name=f'预测数据（{pred_len} 个数据点）',
            increasing_line_color='#66BB6A',
            decreasing_line_color='#FF7043'
        ))
    
    # Add actual data for comparison (if exists)
    if actual_df is not None and len(actual_df) > 0:
        # Actual data should be in the same time period as prediction data
        if 'timestamps' in df.columns:
            # Actual data should use the same timestamps as prediction data to ensure time alignment
            if 'pred_timestamps' in locals():
                actual_timestamps = pred_timestamps
            else:
                # If no prediction timestamps, calculate from the last timestamp of historical data
                if len(historical_df) > 0:
                    last_timestamp = historical_df['timestamps'].iloc[-1]
                    time_diff = df['timestamps'].iloc[1] - df['timestamps'].iloc[0] if len(df) > 1 else pd.Timedelta(hours=1)
                    actual_timestamps = pd.date_range(
                        start=last_timestamp + time_diff,
                        periods=len(actual_df),
                        freq=time_diff
                    )
                else:
                    actual_timestamps = range(len(historical_df), len(historical_df) + len(actual_df))
        else:
            actual_timestamps = range(len(historical_df), len(historical_df) + len(actual_df))
        
        fig.add_trace(go.Candlestick(
            x=actual_timestamps,
            open=actual_df['open'],
            high=actual_df['high'],
            low=actual_df['low'],
            close=actual_df['close'],
            name=f'实际数据（{pred_len} 个数据点）',
            increasing_line_color='#FF9800',
            decreasing_line_color='#F44336'
        ))
    
    # Update layout
    fig.update_layout(
        title=f'Kronos 预测结果 — {lookback} 个历史点 + {pred_len} 个预测点',
        xaxis_title='时间',
        yaxis_title='价格',
        template='plotly_white',
        height=600,
        showlegend=True
    )
    
    # Ensure x-axis time continuity
    if 'timestamps' in historical_df.columns:
        # Get all timestamps and sort them
        all_timestamps = []
        if len(historical_df) > 0:
            all_timestamps.extend(historical_df['timestamps'])
        if 'pred_timestamps' in locals():
            all_timestamps.extend(pred_timestamps)
        if 'actual_timestamps' in locals():
            all_timestamps.extend(actual_timestamps)
        
        if all_timestamps:
            all_timestamps = sorted(all_timestamps)
            fig.update_xaxes(
                range=[all_timestamps[0], all_timestamps[-1]],
                rangeslider_visible=False,
                type='date'
            )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def _normalize_stock_df(df, ts_col, open_col, high_col, low_col, close_col, volume_col=None, amount_col=None):
    """Rename and clean fetched stock dataframe to standard format."""
    df = df.rename(columns={
        ts_col: 'timestamps',
        open_col: 'open',
        high_col: 'high',
        low_col: 'low',
        close_col: 'close',
    })
    if volume_col and volume_col in df.columns:
        df = df.rename(columns={volume_col: 'volume'})
    else:
        df['volume'] = 0.0
    if amount_col and amount_col in df.columns:
        df = df.rename(columns={amount_col: 'amount'})
    else:
        df['amount'] = 0.0

    df['timestamps'] = pd.to_datetime(df['timestamps'])
    for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['open', 'high', 'low', 'close'])
    return df[['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']]


def fetch_stock_akshare(stock_code, period, start_date, end_date):
    """Fetch A-share K-line data via AKShare."""
    if not AKSHARE_AVAILABLE:
        raise Exception("AKShare 未安装，请运行: pip install akshare")

    start_str = start_date.replace('-', '')
    end_str = end_date.replace('-', '')

    if period in ('daily', 'weekly', 'monthly'):
        period_map = {'daily': 'daily', 'weekly': 'weekly', 'monthly': 'monthly'}
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period=period_map[period],
            start_date=start_str,
            end_date=end_str,
            adjust="qfq"
        )
        return _normalize_stock_df(df, '日期', '开盘', '最高', '最低', '收盘', '成交量', '成交额')
    else:
        period_num = period.replace('min', '')
        df = ak.stock_zh_a_hist_min_em(
            symbol=stock_code,
            period=period_num,
            start_date=f"{start_date} 09:30:00",
            end_date=f"{end_date} 15:00:00",
            adjust="qfq"
        )
        return _normalize_stock_df(df, '时间', '开盘', '最高', '最低', '收盘', '成交量', '成交额')


def fetch_stock_tushare(stock_code, period, start_date, end_date, token=''):
    """Fetch A-share K-line data via Tushare Pro."""
    if not TUSHARE_AVAILABLE:
        raise Exception("Tushare 未安装，请运行: pip install tushare")

    token = token.strip() or _load_tushare_token()
    if not token:
        raise Exception("请先配置 Tushare Token（可在 tushare.pro 注册获取）")

    ts.set_token(token)
    pro = ts.pro_api()

    # 转换股票代码格式：600036 → 600036.SH
    if stock_code.startswith('6') or stock_code.startswith('5'):
        ts_code = f"{stock_code}.SH"
    elif stock_code.startswith('4') or stock_code.startswith('8'):
        ts_code = f"{stock_code}.BJ"
    else:
        ts_code = f"{stock_code}.SZ"

    start_str = start_date.replace('-', '')
    end_str = end_date.replace('-', '')

    freq_map = {
        'daily': 'D', 'weekly': 'W', 'monthly': 'M',
        '5min': '5min', '15min': '15min', '30min': '30min', '60min': '60min'
    }
    freq = freq_map.get(period, 'D')

    df = ts.pro_bar(ts_code=ts_code, freq=freq, start_date=start_str, end_date=end_str, adj='qfq')
    if df is None or df.empty:
        raise Exception("未获取到数据，请检查股票代码、日期范围及 Token 权限")

    # 日线/周线/月线用 trade_date，分钟线用 trade_time
    if period in ('daily', 'weekly', 'monthly'):
        df = df.sort_values('trade_date').reset_index(drop=True)
        return _normalize_stock_df(df, 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount')
    else:
        df = df.sort_values('trade_time').reset_index(drop=True)
        return _normalize_stock_df(df, 'trade_time', 'open', 'high', 'low', 'close', 'vol', 'amount')


def _build_data_info(df):
    """Build data_info dict from a standardized DataFrame."""
    if len(df) < 2:
        timeframe = "未知"
    else:
        diffs = [df['timestamps'].iloc[i] - df['timestamps'].iloc[i - 1]
                 for i in range(1, min(10, len(df)))]
        avg = sum(diffs, pd.Timedelta(0)) / len(diffs)
        if avg < pd.Timedelta(minutes=1):
            timeframe = f"{avg.total_seconds():.0f} 秒"
        elif avg < pd.Timedelta(hours=1):
            timeframe = f"{avg.total_seconds() / 60:.0f} 分钟"
        elif avg < pd.Timedelta(days=1):
            timeframe = f"{avg.total_seconds() / 3600:.0f} 小时"
        else:
            timeframe = f"{avg.days} 天"

    return {
        'rows': len(df),
        'columns': list(df.columns),
        'start_date': df['timestamps'].min().isoformat(),
        'end_date': df['timestamps'].max().isoformat(),
        'price_range': {
            'min': float(df[['open', 'high', 'low', 'close']].min().min()),
            'max': float(df[['open', 'high', 'low', 'close']].max().max())
        },
        'prediction_columns': ['open', 'high', 'low', 'close'] + (['volume'] if 'volume' in df.columns else []),
        'timeframe': timeframe
    }


@app.route('/api/fetch-stock', methods=['POST'])
def fetch_stock():
    """Fetch stock K-line data from online data source and save locally."""
    try:
        data = request.get_json()
        stock_code = data.get('stock_code', '').strip()
        data_source = data.get('data_source', 'akshare')
        period = data.get('period', 'daily')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')

        if not stock_code:
            return jsonify({'error': '请输入股票代码'}), 400
        if not start_date or not end_date:
            return jsonify({'error': '请选择开始和结束日期'}), 400
        if start_date >= end_date:
            return jsonify({'error': '结束日期必须晚于开始日期'}), 400

        if data_source == 'akshare':
            df = fetch_stock_akshare(stock_code, period, start_date, end_date)
        elif data_source == 'tushare':
            token = data.get('token', '')
            df = fetch_stock_tushare(stock_code, period, start_date, end_date, token)
        else:
            return jsonify({'error': f'不支持的数据源：{data_source}'}), 400

        if len(df) == 0:
            return jsonify({'error': '未获取到数据，请检查股票代码和日期范围'}), 400

        data_dir = _get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        filename = f"{stock_code}_{period}_{start_date}_{end_date}.csv"
        file_path = os.path.join(data_dir, filename)
        df.to_csv(file_path, index=False, encoding='utf-8')

        return jsonify({
            'success': True,
            'file_path': file_path,
            'data_info': _build_data_info(df),
            'message': f'成功获取 {stock_code} 数据，共 {len(df)} 条记录'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/data-sources')
def get_data_sources():
    """Return availability of online data sources."""
    return jsonify({
        'akshare': AKSHARE_AVAILABLE,
        'tushare': TUSHARE_AVAILABLE,
    })


@app.route('/api/tushare-token', methods=['GET'])
def get_tushare_token():
    token = _load_tushare_token()
    # 脱敏：只返回前4位和后4位
    if len(token) > 8:
        masked = token[:4] + '*' * (len(token) - 8) + token[-4:]
    else:
        masked = '*' * len(token)
    return jsonify({'token': masked, 'configured': bool(token)})


@app.route('/api/tushare-token', methods=['POST'])
def set_tushare_token():
    data = request.get_json()
    token = data.get('token', '').strip()
    if not token:
        return jsonify({'error': 'Token 不能为空'}), 400
    _save_tushare_token(token)
    return jsonify({'success': True, 'message': 'Token 已保存'})


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/api/data-files')
def get_data_files():
    """Get available data file list"""
    data_files = load_data_files()
    return jsonify(data_files)

@app.route('/api/load-data', methods=['POST'])
def load_data():
    """Load data file"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({'error': '文件路径不能为空'}), 400

        df, error = load_data_file(file_path)
        if error:
            return jsonify({'error': error}), 400

        # Detect data time frequency
        def detect_timeframe(df):
            if len(df) < 2:
                return "Unknown"
            
            time_diffs = []
            for i in range(1, min(10, len(df))):  # Check first 10 time differences
                diff = df['timestamps'].iloc[i] - df['timestamps'].iloc[i-1]
                time_diffs.append(diff)
            
            if not time_diffs:
                return "Unknown"
            
            # Calculate average time difference
            avg_diff = sum(time_diffs, pd.Timedelta(0)) / len(time_diffs)
            
            # Convert to readable format
            if avg_diff < pd.Timedelta(minutes=1):
                return f"{avg_diff.total_seconds():.0f} seconds"
            elif avg_diff < pd.Timedelta(hours=1):
                return f"{avg_diff.total_seconds() / 60:.0f} minutes"
            elif avg_diff < pd.Timedelta(days=1):
                return f"{avg_diff.total_seconds() / 3600:.0f} hours"
            else:
                return f"{avg_diff.days} days"
        
        # Return data information
        data_info = {
            'rows': len(df),
            'columns': list(df.columns),
            'start_date': df['timestamps'].min().isoformat() if 'timestamps' in df.columns else 'N/A',
            'end_date': df['timestamps'].max().isoformat() if 'timestamps' in df.columns else 'N/A',
            'price_range': {
                'min': float(df[['open', 'high', 'low', 'close']].min().min()),
                'max': float(df[['open', 'high', 'low', 'close']].max().max())
            },
            'prediction_columns': ['open', 'high', 'low', 'close'] + (['volume'] if 'volume' in df.columns else []),
            'timeframe': detect_timeframe(df)
        }
        
        return jsonify({
            'success': True,
            'data_info': data_info,
            'message': f'数据加载成功，共 {len(df)} 行'
        })
        
    except Exception as e:
        return jsonify({'error': f'数据加载失败：{str(e)}'}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Perform prediction"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        lookback = int(data.get('lookback', 400))
        pred_len = int(data.get('pred_len', 120))
        
        # Get prediction quality parameters
        temperature = float(data.get('temperature', 1.0))
        top_p = float(data.get('top_p', 0.9))
        sample_count = int(data.get('sample_count', 1))
        
        if not file_path:
            return jsonify({'error': '文件路径不能为空'}), 400

        # Load data
        df, error = load_data_file(file_path)
        if error:
            return jsonify({'error': error}), 400
        
        if len(df) < lookback:
            return jsonify({'error': f'数据长度不足，至少需要 {lookback} 行'}), 400
        
        mode = data.get('mode', 'forecast')  # 'forecast' 预测未来 | 'backtest' 回测验证

        if MODEL_AVAILABLE and predictor is not None:
            try:
                required_cols = ['open', 'high', 'low', 'close']
                if 'volume' in df.columns:
                    required_cols.append('volume')

                time_diff = df['timestamps'].iloc[1] - df['timestamps'].iloc[0] if len(df) > 1 else pd.Timedelta(days=1)

                if mode == 'backtest':
                    # 回测模式：取前 lookback 行，预测后续 pred_len 行，与真实数据对比
                    if len(df) < lookback + pred_len:
                        return jsonify({'error': f'回测模式需要至少 {lookback + pred_len} 行数据，当前只有 {len(df)} 行'}), 400
                    x_df = df.iloc[:lookback][required_cols]
                    x_timestamp = df.iloc[:lookback]['timestamps']
                    y_timestamp = df.iloc[lookback:lookback + pred_len]['timestamps']
                    historical_start_idx = 0
                    prediction_type = f"Kronos 回测验证（前 {lookback} 个数据点输入，对比后续 {pred_len} 个真实点）"
                else:
                    # 预测模式：取最后 lookback 行，预测未来 pred_len 个时间点
                    x_df = df.iloc[-lookback:][required_cols]
                    x_timestamp = df.iloc[-lookback:]['timestamps']
                    y_timestamp = pd.Series(
                        pd.date_range(start=df['timestamps'].iloc[-1] + time_diff, periods=pred_len, freq=time_diff),
                        name='timestamps'
                    )
                    historical_start_idx = len(df) - lookback
                    prediction_type = f"Kronos 预测（最近 {lookback} 个数据点输入，预测未来 {pred_len} 个点）"

                if isinstance(x_timestamp, pd.DatetimeIndex):
                    x_timestamp = pd.Series(x_timestamp, name='timestamps')
                if isinstance(y_timestamp, pd.DatetimeIndex):
                    y_timestamp = pd.Series(y_timestamp, name='timestamps')

                pred_df = predictor.predict(
                    df=x_df,
                    x_timestamp=x_timestamp,
                    y_timestamp=y_timestamp,
                    pred_len=pred_len,
                    T=temperature,
                    top_p=top_p,
                    sample_count=sample_count
                )

            except Exception as e:
                return jsonify({'error': f'Kronos 模型预测失败：{str(e)}'}), 500
        else:
            return jsonify({'error': 'Kronos 模型未加载，请先加载模型'}), 400

        # 回测模式：收集真实对比数据；预测模式：无对比
        actual_data = []
        actual_df = None
        if mode == 'backtest':
            actual_df = df.iloc[lookback:lookback + pred_len]
            for _, row in actual_df.iterrows():
                actual_data.append({
                    'timestamp': row['timestamps'].isoformat(),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume']) if 'volume' in row else 0,
                    'amount': float(row['amount']) if 'amount' in row else 0
                })

        chart_json = create_prediction_chart(df, pred_df, lookback, pred_len, actual_df, historical_start_idx)

        # 预测结果时间戳
        if mode == 'backtest':
            future_timestamps = df.iloc[lookback:lookback + pred_len]['timestamps'].reset_index(drop=True)
        elif 'timestamps' in df.columns and len(df) > 1:
            future_timestamps = pd.date_range(start=df['timestamps'].iloc[-1] + time_diff, periods=pred_len, freq=time_diff)
        else:
            future_timestamps = range(lookback, lookback + pred_len)
        
        prediction_results = []
        for i, (_, row) in enumerate(pred_df.iterrows()):
            prediction_results.append({
                'timestamp': future_timestamps[i].isoformat() if i < len(future_timestamps) else f"T{i}",
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume']) if 'volume' in row else 0,
                'amount': float(row['amount']) if 'amount' in row else 0
            })
        
        # Save prediction results to file
        try:
            save_prediction_results(
                file_path=file_path,
                prediction_type=prediction_type,
                prediction_results=prediction_results,
                actual_data=actual_data,
                input_data=x_df,
                prediction_params={
                    'lookback': lookback,
                    'pred_len': pred_len,
                    'temperature': temperature,
                    'top_p': top_p,
                    'sample_count': sample_count,
                    'mode': mode
                }
            )
        except Exception as e:
            print(f"Failed to save prediction results: {e}")
        
        return jsonify({
            'success': True,
            'prediction_type': prediction_type,
            'chart': chart_json,
            'prediction_results': prediction_results,
            'actual_data': actual_data,
            'has_comparison': len(actual_data) > 0,
            'message': f'预测完成，生成了 {pred_len} 个预测点' + (f'，包含 {len(actual_data)} 个真实数据点用于对比' if actual_data else '')
        })
        
    except Exception as e:
        return jsonify({'error': f'预测失败：{str(e)}'}), 500

@app.route('/api/load-model', methods=['POST'])
def load_model():
    """Load Kronos model"""
    global tokenizer, model, predictor
    
    try:
        if not MODEL_AVAILABLE:
            return jsonify({'error': f'Kronos 模型库不可用，请查看 %APPDATA%\\KronosWebUI\\model_import_error.log 了解详情'}), 400
        
        data = request.get_json()
        model_key = data.get('model_key', 'kronos-small')
        device = data.get('device', 'cpu')
        
        if model_key not in AVAILABLE_MODELS:
            return jsonify({'error': f'不支持的模型：{model_key}'}), 400
        
        model_config = AVAILABLE_MODELS[model_key]
        
        # Load tokenizer and model
        tokenizer = KronosTokenizer.from_pretrained(model_config['tokenizer_id'])
        model = Kronos.from_pretrained(model_config['model_id'])
        
        # Create predictor
        predictor = KronosPredictor(model, tokenizer, device=device, max_context=model_config['context_length'])
        
        return jsonify({
            'success': True,
            'message': f'模型加载成功：{model_config["name"]}（{model_config["params"]}）运行于 {device}',
            'model_info': {
                'name': model_config['name'],
                'params': model_config['params'],
                'context_length': model_config['context_length'],
                'description': model_config['description']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'模型加载失败：{str(e)}'}), 500

@app.route('/api/available-models')
def get_available_models():
    """Get available model list"""
    return jsonify({
        'models': AVAILABLE_MODELS,
        'model_available': MODEL_AVAILABLE
    })

@app.route('/api/model-status')
def get_model_status():
    """Get model status"""
    if MODEL_AVAILABLE:
        if predictor is not None:
            return jsonify({
                'available': True,
                'loaded': True,
                'message': 'Kronos 模型已加载并可用',
                'current_model': {
                    'name': predictor.model.__class__.__name__,
                    'device': str(next(predictor.model.parameters()).device)
                }
            })
        else:
            return jsonify({
                'available': True,
                'loaded': False,
                'message': 'Kronos 模型可用但未加载'
            })
    else:
        return jsonify({
            'available': False,
            'loaded': False,
            'message': 'Kronos 模型库不可用，请安装相关依赖'
        })

if __name__ == '__main__':
    print("Starting Kronos Web UI...")
    print(f"Model availability: {MODEL_AVAILABLE}")
    if MODEL_AVAILABLE:
        print("Tip: You can load Kronos model through /api/load-model endpoint")
    else:
        print("Tip: Will use simulated data for demonstration")
    
    app.run(debug=True, host='0.0.0.0', port=7070)
