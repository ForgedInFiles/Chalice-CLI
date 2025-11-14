"""
Workflow Automation Engine
Create and execute automated workflows with triggers and actions
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import threading
import time
import schedule


class TriggerType(Enum):
    """Workflow trigger types"""
    SCHEDULE = "schedule"  # Time-based trigger
    EVENT = "event"  # Event-based trigger
    MANUAL = "manual"  # Manual execution
    CONDITION = "condition"  # Condition-based trigger


class ActionType(Enum):
    """Workflow action types"""
    COMMAND = "command"  # Execute a command
    TOOL = "tool"  # Call a tool
    AGENT = "agent"  # Invoke an agent
    SCRIPT = "script"  # Run a script
    NOTIFICATION = "notification"  # Send notification
    HTTP = "http"  # HTTP request


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowTrigger:
    """Workflow trigger definition"""

    def __init__(self, trigger_type: TriggerType, config: Dict[str, Any]):
        self.type = trigger_type
        self.config = config

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type.value,
            'config': self.config
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'WorkflowTrigger':
        return WorkflowTrigger(
            TriggerType(data['type']),
            data['config']
        )


class WorkflowAction:
    """Workflow action definition"""

    def __init__(
        self,
        action_type: ActionType,
        config: Dict[str, Any],
        name: str = ""
    ):
        self.type = action_type
        self.config = config
        self.name = name or f"{action_type.value}_action"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type.value,
            'name': self.name,
            'config': self.config
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'WorkflowAction':
        return WorkflowAction(
            ActionType(data['type']),
            data['config'],
            data.get('name', '')
        )


class Workflow:
    """Workflow definition"""

    def __init__(
        self,
        name: str,
        description: str = "",
        triggers: List[WorkflowTrigger] = None,
        actions: List[WorkflowAction] = None,
        enabled: bool = True
    ):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.name = name
        self.description = description
        self.triggers = triggers or []
        self.actions = actions or []
        self.enabled = enabled
        self.created_at = datetime.now().isoformat()
        self.last_run = None
        self.run_count = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'triggers': [t.to_dict() for t in self.triggers],
            'actions': [a.to_dict() for a in self.actions],
            'enabled': self.enabled,
            'created_at': self.created_at,
            'last_run': self.last_run,
            'run_count': self.run_count
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Workflow':
        workflow = Workflow(
            data['name'],
            data.get('description', ''),
            [WorkflowTrigger.from_dict(t) for t in data.get('triggers', [])],
            [WorkflowAction.from_dict(a) for a in data.get('actions', [])],
            data.get('enabled', True)
        )
        workflow.id = data.get('id', workflow.id)
        workflow.created_at = data.get('created_at', workflow.created_at)
        workflow.last_run = data.get('last_run')
        workflow.run_count = data.get('run_count', 0)
        return workflow


class WorkflowExecution:
    """Workflow execution record"""

    def __init__(self, workflow_id: str):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.workflow_id = workflow_id
        self.status = WorkflowStatus.PENDING
        self.started_at = datetime.now().isoformat()
        self.completed_at = None
        self.results: List[Dict[str, Any]] = []
        self.error = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'status': self.status.value,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'results': self.results,
            'error': self.error
        }


class WorkflowEngine:
    """
    Workflow automation engine

    Create, manage, and execute automated workflows
    """

    def __init__(self, workflows_dir: Optional[Path] = None):
        """Initialize workflow engine"""
        if workflows_dir is None:
            workflows_dir = Path(__file__).parent / "workflows"

        self.workflows_dir = Path(workflows_dir)
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

        self.workflows: Dict[str, Workflow] = {}
        self.executions: List[WorkflowExecution] = []
        self.running = False
        self.scheduler_thread = None

        self.action_handlers: Dict[ActionType, Callable] = {}

        self._load_workflows()
        self._register_default_handlers()

    def _load_workflows(self):
        """Load workflows from disk"""
        workflow_file = self.workflows_dir / "workflows.json"
        if not workflow_file.exists():
            return

        try:
            with open(workflow_file, 'r') as f:
                data = json.load(f)

            for workflow_data in data:
                workflow = Workflow.from_dict(workflow_data)
                self.workflows[workflow.id] = workflow

        except Exception as e:
            print(f"Error loading workflows: {e}")

    def _save_workflows(self):
        """Save workflows to disk"""
        workflow_file = self.workflows_dir / "workflows.json"

        try:
            data = [w.to_dict() for w in self.workflows.values()]

            with open(workflow_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error saving workflows: {e}")

    def _register_default_handlers(self):
        """Register default action handlers"""
        self.register_action_handler(ActionType.COMMAND, self._handle_command)
        self.register_action_handler(ActionType.SCRIPT, self._handle_script)
        self.register_action_handler(ActionType.NOTIFICATION, self._handle_notification)

    def _handle_command(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle command action"""
        import subprocess

        try:
            command = action.config.get('command', '')
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=action.config.get('timeout', 30)
            )

            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _handle_script(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle script action"""
        try:
            script = action.config.get('script', '')
            # Execute script with context
            exec_globals = {'context': context, 'result': None}
            exec(script, exec_globals)

            return {
                'success': True,
                'result': exec_globals.get('result')
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _handle_notification(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle notification action"""
        message = action.config.get('message', '')
        print(f"[NOTIFICATION] {message}")

        return {
            'success': True,
            'message': message
        }

    def register_action_handler(
        self,
        action_type: ActionType,
        handler: Callable[[WorkflowAction, Dict[str, Any]], Dict[str, Any]]
    ):
        """Register custom action handler"""
        self.action_handlers[action_type] = handler

    def create_workflow(
        self,
        name: str,
        description: str = "",
        triggers: List[WorkflowTrigger] = None,
        actions: List[WorkflowAction] = None
    ) -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(name, description, triggers, actions)
        self.workflows[workflow.id] = workflow
        self._save_workflows()

        print(f"✓ Created workflow: {name} (ID: {workflow.id})")
        return workflow

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            self._save_workflows()
            print(f"✓ Deleted workflow: {workflow_id}")
            return True

        return False

    def enable_workflow(self, workflow_id: str):
        """Enable a workflow"""
        if workflow_id in self.workflows:
            self.workflows[workflow_id].enabled = True
            self._save_workflows()

    def disable_workflow(self, workflow_id: str):
        """Disable a workflow"""
        if workflow_id in self.workflows:
            self.workflows[workflow_id].enabled = False
            self._save_workflows()

    def execute_workflow(
        self,
        workflow_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        """Execute a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.workflows[workflow_id]
        execution = WorkflowExecution(workflow_id)
        execution.status = WorkflowStatus.RUNNING

        context = context or {}

        try:
            # Execute actions in sequence
            for action in workflow.actions:
                if action.type not in self.action_handlers:
                    result = {
                        'success': False,
                        'error': f"No handler for action type: {action.type.value}"
                    }
                else:
                    handler = self.action_handlers[action.type]
                    result = handler(action, context)

                execution.results.append({
                    'action': action.name,
                    'result': result
                })

                # Stop on failure if configured
                if not result.get('success') and not action.config.get('continue_on_error', False):
                    break

            execution.status = WorkflowStatus.COMPLETED
            workflow.last_run = datetime.now().isoformat()
            workflow.run_count += 1

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)

        execution.completed_at = datetime.now().isoformat()
        self.executions.append(execution)
        self._save_workflows()

        return execution

    def start_scheduler(self):
        """Start workflow scheduler"""
        if self.running:
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()

        print("✓ Workflow scheduler started")

    def stop_scheduler(self):
        """Stop workflow scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

        print("✓ Workflow scheduler stopped")

    def _scheduler_loop(self):
        """Scheduler main loop"""
        # Setup scheduled workflows
        for workflow in self.workflows.values():
            if not workflow.enabled:
                continue

            for trigger in workflow.triggers:
                if trigger.type == TriggerType.SCHEDULE:
                    self._schedule_workflow(workflow, trigger)

        # Run scheduler
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def _schedule_workflow(self, workflow: Workflow, trigger: WorkflowTrigger):
        """Schedule a workflow based on trigger"""
        interval = trigger.config.get('interval', 'daily')
        time_str = trigger.config.get('time', '09:00')

        if interval == 'daily':
            schedule.every().day.at(time_str).do(
                lambda: self.execute_workflow(workflow.id)
            )
        elif interval == 'hourly':
            schedule.every().hour.do(
                lambda: self.execute_workflow(workflow.id)
            )
        elif interval == 'weekly':
            day = trigger.config.get('day', 'monday')
            getattr(schedule.every(), day).at(time_str).do(
                lambda: self.execute_workflow(workflow.id)
            )

    def get_execution_history(
        self,
        workflow_id: Optional[str] = None,
        limit: int = 10
    ) -> List[WorkflowExecution]:
        """Get execution history"""
        executions = self.executions

        if workflow_id:
            executions = [e for e in executions if e.workflow_id == workflow_id]

        return sorted(
            executions,
            key=lambda e: e.started_at,
            reverse=True
        )[:limit]


# Global workflow engine instance
_workflow_engine = None


def get_workflow_engine() -> WorkflowEngine:
    """Get global workflow engine instance"""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine
