"""
Performance Monitor Component - System monitoring and error handling
"""
from nicegui import ui
from typing import Dict, Any, List, Optional
import time
import asyncio
from datetime import datetime, timedelta

class PerformanceMonitor:
    """Performance monitoring and error handling system"""
    
    def __init__(self):
        """Initialize the performance monitor"""
        self.metrics = {
            'response_times': [],
            'error_counts': {},
            'tool_execution_times': {},
            'session_load_times': [],
            'memory_usage': [],
            'start_time': time.time()
        }
        self.error_log = []
        self.performance_alerts = []
        self.max_response_time = 10.0  # seconds
        self.max_memory_usage = 100  # MB
    
    def start_timer(self, operation: str) -> float:
        """Start timing an operation"""
        return time.time()
    
    def end_timer(self, operation: str, start_time: float):
        """End timing an operation and record metrics"""
        duration = time.time() - start_time
        
        if operation == 'ai_response':
            self.metrics['response_times'].append(duration)
            # Keep only last 100 measurements
            if len(self.metrics['response_times']) > 100:
                self.metrics['response_times'].pop(0)
            
            # Check for performance alerts
            if duration > self.max_response_time:
                self._add_performance_alert(f'AI response time ({duration:.2f}s) exceeded threshold ({self.max_response_time}s)')
        
        elif operation == 'tool_execution':
            if operation not in self.metrics['tool_execution_times']:
                self.metrics['tool_execution_times'][operation] = []
            self.metrics['tool_execution_times'][operation].append(duration)
            
            # Keep only last 50 measurements per tool
            if len(self.metrics['tool_execution_times'][operation]) > 50:
                self.metrics['tool_execution_times'][operation].pop(0)
        
        elif operation == 'session_load':
            self.metrics['session_load_times'].append(duration)
            if len(self.metrics['session_load_times']) > 50:
                self.metrics['session_load_times'].pop(0)
    
    def record_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Record an error for monitoring"""
        error_entry = {
            'timestamp': datetime.now(),
            'type': error_type,
            'message': error_message,
            'context': context or {}
        }
        
        self.error_log.append(error_entry)
        
        # Keep only last 100 errors
        if len(self.error_log) > 100:
            self.error_log.pop(0)
        
        # Update error counts
        if error_type not in self.metrics['error_counts']:
            self.metrics['error_counts'][error_type] = 0
        self.metrics['error_counts'][error_type] += 1
        
        # Check for error rate alerts
        self._check_error_rate_alerts()
    
    def _check_error_rate_alerts(self):
        """Check if error rates are concerning"""
        total_errors = sum(self.metrics['error_counts'].values())
        uptime = time.time() - self.metrics['start_time']
        error_rate = total_errors / (uptime / 3600)  # errors per hour
        
        if error_rate > 10:  # More than 10 errors per hour
            self._add_performance_alert(f'High error rate detected: {error_rate:.1f} errors/hour')
    
    def _add_performance_alert(self, message: str):
        """Add a performance alert"""
        alert = {
            'timestamp': datetime.now(),
            'message': message,
            'severity': 'warning'
        }
        
        self.performance_alerts.append(alert)
        
        # Keep only last 50 alerts
        if len(self.performance_alerts) > 50:
            self.performance_alerts.pop(0)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics"""
        uptime = time.time() - self.metrics['start_time']
        
        summary = {
            'uptime_seconds': uptime,
            'uptime_formatted': str(timedelta(seconds=int(uptime))),
            'total_errors': sum(self.metrics['error_counts'].values()),
            'error_rate_per_hour': sum(self.metrics['error_counts'].values()) / (uptime / 3600) if uptime > 0 else 0
        }
        
        # AI response time statistics
        if self.metrics['response_times']:
            summary['ai_response_time'] = {
                'average': sum(self.metrics['response_times']) / len(self.metrics['response_times']),
                'min': min(self.metrics['response_times']),
                'max': max(self.metrics['response_times']),
                'count': len(self.metrics['response_times'])
            }
        
        # Tool execution statistics
        if self.metrics['tool_execution_times']:
            summary['tool_performance'] = {}
            for tool, times in self.metrics['tool_execution_times'].items():
                if times:
                    summary['tool_performance'][tool] = {
                        'average': sum(times) / len(times),
                        'min': min(times),
                        'max': max(times),
                        'count': len(times)
                    }
        
        # Session load statistics
        if self.metrics['session_load_times']:
            summary['session_load_time'] = {
                'average': sum(self.metrics['session_load_times']) / len(self.metrics['session_load_times']),
                'min': min(self.metrics['session_load_times']),
                'max': max(self.metrics['session_load_times']),
                'count': len(self.metrics['session_load_times'])
            }
        
        return summary
    
    def show_performance_dashboard(self):
        """Show the performance monitoring dashboard"""
        with ui.dialog() as dashboard_dialog, ui.card().classes('w-full max-w-4xl max-h-[90vh]'):
            # Header
            with ui.row().classes('items-center justify-between mb-6'):
                ui.label('📊 Performance Dashboard').classes('text-2xl font-bold text-gray-800')
                ui.button('✕', on_click=dashboard_dialog.close).classes(
                    'w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300'
                )
            
            # Refresh button
            with ui.row().classes('justify-end mb-4'):
                ui.button('🔄 Refresh', on_click=lambda: self._refresh_dashboard(content_container)).classes(
                    'px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded'
                )
            
            # Content area
            with ui.column().classes('overflow-y-auto') as content_container:
                self._show_dashboard_content(content_container)
            
            dashboard_dialog.open()
    
    def _show_dashboard_content(self, content_container):
        """Show the dashboard content"""
        content_container.clear()
        
        with content_container:
            # System Overview
            with ui.card().classes('mb-6 p-4 bg-blue-50 border border-blue-200'):
                ui.label('🖥️ System Overview').classes('text-lg font-semibold text-blue-800 mb-3')
                
                summary = self.get_performance_summary()
                
                with ui.row().classes('flex-wrap gap-6'):
                    with ui.column():
                        ui.label('Uptime').classes('text-sm text-blue-600 font-medium')
                        ui.label(summary['uptime_formatted']).classes('text-lg font-bold text-blue-800')
                    
                    with ui.column():
                        ui.label('Total Errors').classes('text-sm text-blue-600 font-medium')
                        ui.label(str(summary['total_errors'])).classes('text-lg font-bold text-blue-800')
                    
                    with ui.column():
                        ui.label('Error Rate').classes('text-sm text-blue-600 font-medium')
                        ui.label(f"{summary['error_rate_per_hour']:.1f}/hour").classes('text-lg font-bold text-blue-800')
            
            # AI Performance
            if 'ai_response_time' in summary:
                with ui.card().classes('mb-6 p-4 bg-green-50 border border-green-200'):
                    ui.label('🤖 AI Response Performance').classes('text-lg font-semibold text-green-800 mb-3')
                    
                    ai_stats = summary['ai_response_time']
                    with ui.row().classes('flex-wrap gap-6'):
                        with ui.column():
                            ui.label('Average Response Time').classes('text-sm text-green-600 font-medium')
                            ui.label(f"{ai_stats['average']:.2f}s").classes('text-lg font-bold text-green-800')
                        
                        with ui.column():
                            ui.label('Fastest Response').classes('text-sm text-green-600 font-medium')
                            ui.label(f"{ai_stats['min']:.2f}s").classes('text-lg font-bold text-green-800')
                        
                        with ui.column():
                            ui.label('Slowest Response').classes('text-sm text-green-600 font-medium')
                            ui.label(f"{ai_stats['max']:.2f}s").classes('text-lg font-bold text-green-800')
                        
                        with ui.column():
                            ui.label('Total Requests').classes('text-sm text-green-600 font-medium')
                            ui.label(str(ai_stats['count'])).classes('text-lg font-bold text-green-800')
            
            # Tool Performance
            if 'tool_performance' in summary:
                with ui.card().classes('mb-6 p-4 bg-purple-50 border border-purple-200'):
                    ui.label('🛠️ Tool Performance').classes('text-lg font-semibold text-purple-800 mb-3')
                    
                    for tool, stats in summary['tool_performance'].items():
                        with ui.expansion(f"{tool.replace('_', ' ').title()}", icon='settings').classes('mb-2'):
                            with ui.row().classes('flex-wrap gap-4'):
                                with ui.column():
                                    ui.label('Average Time').classes('text-sm text-purple-600 font-medium')
                                    ui.label(f"{stats['average']:.3f}s").classes('font-bold text-purple-800')
                                
                                with ui.column():
                                    ui.label('Fastest').classes('text-sm text-purple-600 font-medium')
                                    ui.label(f"{stats['min']:.3f}s").classes('font-bold text-purple-800')
                                
                                with ui.column():
                                    ui.label('Slowest').classes('text-sm text-purple-600 font-medium')
                                    ui.label(f"{stats['max']:.3f}s").classes('font-bold text-purple-800')
                                
                                with ui.column():
                                    ui.label('Total Uses').classes('text-sm text-purple-600 font-medium')
                                    ui.label(str(stats['count'])).classes('font-bold text-purple-800')
            
            # Recent Errors
            if self.error_log:
                with ui.card().classes('mb-6 p-4 bg-red-50 border border-red-200'):
                    ui.label('❌ Recent Errors').classes('text-lg font-semibold text-red-800 mb-3')
                    
                    # Show last 10 errors
                    for error in self.error_log[-10:]:
                        with ui.expansion(f"{error['type']} - {error['timestamp'].strftime('%H:%M:%S')}", icon='error').classes('mb-2'):
                            ui.label(error['message']).classes('text-red-700 mb-2')
                            if error['context']:
                                ui.label('Context:').classes('text-sm font-medium text-red-600')
                                ui.code(str(error['context'])).classes('text-xs')
            
            # Performance Alerts
            if self.performance_alerts:
                with ui.card().classes('mb-6 p-4 bg-yellow-50 border border-yellow-200'):
                    ui.label('⚠️ Performance Alerts').classes('text-lg font-semibold text-yellow-800 mb-3')
                    
                    # Show last 10 alerts
                    for alert in self.performance_alerts[-10:]:
                        with ui.row().classes('items-center mb-2'):
                            ui.label('⚠️').classes('mr-2')
                            ui.label(alert['message']).classes('text-yellow-700')
                            ui.label(alert['timestamp'].strftime('%H:%M:%S')).classes('text-xs text-yellow-600 ml-auto')
    
    def _refresh_dashboard(self, content_container):
        """Refresh the dashboard content"""
        self._show_dashboard_content(content_container)
    
    def get_health_status(self) -> str:
        """Get overall system health status"""
        summary = self.get_performance_summary()
        
        # Check various health indicators
        if summary['error_rate_per_hour'] > 20:
            return 'critical'
        elif summary['error_rate_per_hour'] > 10:
            return 'warning'
        elif summary['error_rate_per_hour'] > 5:
            return 'degraded'
        else:
            return 'healthy'
    
    def show_health_indicator(self):
        """Show a health status indicator"""
        status = self.get_health_status()
        
        status_config = {
            'healthy': {'color': 'text-green-600', 'icon': '🟢', 'text': 'Healthy'},
            'degraded': {'color': 'text-yellow-600', 'icon': '🟡', 'text': 'Degraded'},
            'warning': {'color': 'text-orange-600', 'icon': '🟠', 'text': 'Warning'},
            'critical': {'color': 'text-red-600', 'icon': '🔴', 'text': 'Critical'}
        }
        
        config = status_config.get(status, status_config['healthy'])
        
        with ui.row().classes('items-center gap-2'):
            ui.label(config['icon']).classes('text-lg')
            ui.label(config['text']).classes(f"text-sm font-medium {config['color']}")
    
    def cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory bloat"""
        current_time = time.time()
        
        # Remove metrics older than 24 hours
        cutoff_time = current_time - (24 * 3600)
        
        # Clean up response times (keep only recent ones)
        self.metrics['response_times'] = [t for t in self.metrics['response_times'] if t > cutoff_time]
        
        # Clean up tool execution times
        for tool in list(self.metrics['tool_execution_times'].keys()):
            self.metrics['tool_execution_times'][tool] = [t for t in self.metrics['tool_execution_times'][tool] if t > cutoff_time]
        
        # Clean up session load times
        self.metrics['session_load_times'] = [t for t in self.metrics['session_load_times'] if t > cutoff_time]
        
        # Clean up old errors (keep only last 50)
        if len(self.error_log) > 50:
            self.error_log = self.error_log[-50:]
        
        # Clean up old alerts (keep only last 25)
        if len(self.performance_alerts) > 25:
            self.performance_alerts = self.performance_alerts[-25:]
