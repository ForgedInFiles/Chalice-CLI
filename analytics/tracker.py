"""
Analytics Tracker
Track usage, costs, and performance metrics
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class AnalyticsTracker:
    """
    Analytics and usage tracking

    Tracks:
    - API calls and costs
    - Token usage
    - Model performance
    - User interactions
    - Error rates
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize analytics tracker"""
        if storage_path is None:
            storage_path = Path(__file__).parent / "data"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.events: List[Dict[str, Any]] = []
        self.events_file = self.storage_path / "events.json"

        self._load_events()

    def _load_events(self):
        """Load events from disk"""
        if not self.events_file.exists():
            return

        try:
            with open(self.events_file, 'r') as f:
                self.events = json.load(f)
        except Exception as e:
            print(f"Error loading events: {e}")

    def _save_events(self):
        """Save events to disk"""
        try:
            with open(self.events_file, 'w') as f:
                json.dump(self.events, f, indent=2)
        except Exception as e:
            print(f"Error saving events: {e}")

    def track_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        user_id: str = "default"
    ):
        """Track an event"""
        event = {
            'type': event_type,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }

        self.events.append(event)

        # Save periodically (every 10 events)
        if len(self.events) % 10 == 0:
            self._save_events()

    def track_api_call(
        self,
        provider: str,
        model: str,
        tokens: int,
        cost: float,
        latency: float,
        success: bool = True
    ):
        """Track API call"""
        self.track_event('api_call', {
            'provider': provider,
            'model': model,
            'tokens': tokens,
            'cost': cost,
            'latency': latency,
            'success': success
        })

    def track_tool_usage(
        self,
        tool_name: str,
        server: str,
        success: bool = True,
        execution_time: float = 0.0
    ):
        """Track tool usage"""
        self.track_event('tool_usage', {
            'tool': tool_name,
            'server': server,
            'success': success,
            'execution_time': execution_time
        })

    def track_agent_usage(
        self,
        agent_name: str,
        success: bool = True,
        execution_time: float = 0.0
    ):
        """Track agent usage"""
        self.track_event('agent_usage', {
            'agent': agent_name,
            'success': success,
            'execution_time': execution_time
        })

    def track_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Track error"""
        self.track_event('error', {
            'error_type': error_type,
            'message': error_message,
            'context': context or {}
        })

    def get_usage_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get usage statistics

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            Usage statistics dictionary
        """
        events = self._filter_events_by_date(start_date, end_date)

        stats = {
            'total_events': len(events),
            'api_calls': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'tool_usage': defaultdict(int),
            'agent_usage': defaultdict(int),
            'errors': 0,
            'by_provider': defaultdict(lambda: {
                'calls': 0,
                'tokens': 0,
                'cost': 0.0
            }),
            'by_model': defaultdict(lambda: {
                'calls': 0,
                'tokens': 0,
                'cost': 0.0
            })
        }

        for event in events:
            event_type = event['type']
            data = event['data']

            if event_type == 'api_call':
                stats['api_calls'] += 1
                stats['total_tokens'] += data.get('tokens', 0)
                stats['total_cost'] += data.get('cost', 0.0)

                provider = data.get('provider', 'unknown')
                model = data.get('model', 'unknown')

                stats['by_provider'][provider]['calls'] += 1
                stats['by_provider'][provider]['tokens'] += data.get('tokens', 0)
                stats['by_provider'][provider]['cost'] += data.get('cost', 0.0)

                stats['by_model'][model]['calls'] += 1
                stats['by_model'][model]['tokens'] += data.get('tokens', 0)
                stats['by_model'][model]['cost'] += data.get('cost', 0.0)

            elif event_type == 'tool_usage':
                tool = data.get('tool', 'unknown')
                stats['tool_usage'][tool] += 1

            elif event_type == 'agent_usage':
                agent = data.get('agent', 'unknown')
                stats['agent_usage'][agent] += 1

            elif event_type == 'error':
                stats['errors'] += 1

        # Convert defaultdicts to regular dicts
        stats['tool_usage'] = dict(stats['tool_usage'])
        stats['agent_usage'] = dict(stats['agent_usage'])
        stats['by_provider'] = dict(stats['by_provider'])
        stats['by_model'] = dict(stats['by_model'])

        return stats

    def get_cost_breakdown(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get cost breakdown"""
        events = self._filter_events_by_date(start_date, end_date)
        api_calls = [e for e in events if e['type'] == 'api_call']

        breakdown = {
            'total_cost': 0.0,
            'by_provider': defaultdict(float),
            'by_model': defaultdict(float),
            'by_date': defaultdict(float)
        }

        for event in api_calls:
            data = event['data']
            cost = data.get('cost', 0.0)
            provider = data.get('provider', 'unknown')
            model = data.get('model', 'unknown')
            date = event['timestamp'].split('T')[0]

            breakdown['total_cost'] += cost
            breakdown['by_provider'][provider] += cost
            breakdown['by_model'][model] += cost
            breakdown['by_date'][date] += cost

        breakdown['by_provider'] = dict(breakdown['by_provider'])
        breakdown['by_model'] = dict(breakdown['by_model'])
        breakdown['by_date'] = dict(breakdown['by_date'])

        return breakdown

    def get_performance_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get performance metrics"""
        events = self._filter_events_by_date(start_date, end_date)

        api_calls = [e for e in events if e['type'] == 'api_call']
        tool_calls = [e for e in events if e['type'] == 'tool_usage']
        agent_calls = [e for e in events if e['type'] == 'agent_usage']

        metrics = {
            'api_latency': {
                'avg': 0.0,
                'min': float('inf'),
                'max': 0.0
            },
            'tool_execution_time': {
                'avg': 0.0,
                'min': float('inf'),
                'max': 0.0
            },
            'agent_execution_time': {
                'avg': 0.0,
                'min': float('inf'),
                'max': 0.0
            },
            'success_rate': {
                'api': 0.0,
                'tools': 0.0,
                'agents': 0.0
            }
        }

        # API latency
        if api_calls:
            latencies = [e['data'].get('latency', 0) for e in api_calls]
            metrics['api_latency']['avg'] = sum(latencies) / len(latencies)
            metrics['api_latency']['min'] = min(latencies)
            metrics['api_latency']['max'] = max(latencies)

            successful = sum(1 for e in api_calls if e['data'].get('success', True))
            metrics['success_rate']['api'] = successful / len(api_calls) * 100

        # Tool execution time
        if tool_calls:
            exec_times = [e['data'].get('execution_time', 0) for e in tool_calls]
            metrics['tool_execution_time']['avg'] = sum(exec_times) / len(exec_times)
            metrics['tool_execution_time']['min'] = min(exec_times)
            metrics['tool_execution_time']['max'] = max(exec_times)

            successful = sum(1 for e in tool_calls if e['data'].get('success', True))
            metrics['success_rate']['tools'] = successful / len(tool_calls) * 100

        # Agent execution time
        if agent_calls:
            exec_times = [e['data'].get('execution_time', 0) for e in agent_calls]
            metrics['agent_execution_time']['avg'] = sum(exec_times) / len(exec_times)
            metrics['agent_execution_time']['min'] = min(exec_times)
            metrics['agent_execution_time']['max'] = max(exec_times)

            successful = sum(1 for e in agent_calls if e['data'].get('success', True))
            metrics['success_rate']['agents'] = successful / len(agent_calls) * 100

        return metrics

    def get_error_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get error report"""
        events = self._filter_events_by_date(start_date, end_date)
        errors = [e for e in events if e['type'] == 'error']

        report = {
            'total_errors': len(errors),
            'by_type': defaultdict(int),
            'recent_errors': []
        }

        for error in errors:
            error_type = error['data'].get('error_type', 'unknown')
            report['by_type'][error_type] += 1

        report['by_type'] = dict(report['by_type'])

        # Get 10 most recent errors
        recent = sorted(errors, key=lambda e: e['timestamp'], reverse=True)[:10]
        report['recent_errors'] = [
            {
                'timestamp': e['timestamp'],
                'type': e['data'].get('error_type'),
                'message': e['data'].get('message')
            }
            for e in recent
        ]

        return report

    def _filter_events_by_date(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Filter events by date range"""
        if start_date is None and end_date is None:
            return self.events

        filtered = []
        for event in self.events:
            event_date = datetime.fromisoformat(event['timestamp'])

            if start_date and event_date < start_date:
                continue

            if end_date and event_date > end_date:
                continue

            filtered.append(event)

        return filtered

    def export_to_csv(self, filename: str):
        """Export events to CSV"""
        import csv

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Type', 'User', 'Data'])

            for event in self.events:
                writer.writerow([
                    event['timestamp'],
                    event['type'],
                    event['user_id'],
                    json.dumps(event['data'])
                ])

        print(f"✓ Exported {len(self.events)} events to {filename}")


# Global analytics tracker instance
_analytics_tracker = None


def get_analytics_tracker() -> AnalyticsTracker:
    """Get global analytics tracker instance"""
    global _analytics_tracker
    if _analytics_tracker is None:
        _analytics_tracker = AnalyticsTracker()
    return _analytics_tracker
