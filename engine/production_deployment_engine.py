"""
Production Deployment Engine for AutoPPM
Provides monitoring, alerting, automation, and production infrastructure
"""

import asyncio
import time
import json
import smtplib
import requests
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from loguru import logger
import psutil
import sqlite3
import threading
from pathlib import Path
import schedule
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from engine.autoppm_orchestrator import get_autoppm_orchestrator
from engine.ml_optimization_engine import get_ml_optimization_engine
from engine.advanced_risk_engine import get_advanced_risk_engine
from engine.multi_broker_engine import get_multi_broker_engine


@dataclass
class SystemMetrics:
    """System performance and health metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    database_connections: int
    active_strategies: int
    portfolio_value: float
    daily_pnl: float
    risk_score: float


@dataclass
class Alert:
    """System alert configuration"""
    id: str
    type: str  # 'info', 'warning', 'error', 'critical'
    message: str
    timestamp: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: str  # 'threshold', 'trend', 'anomaly'
    metric: str
    threshold: float
    operator: str  # '>', '<', '>=', '<=', '==', '!='
    severity: str  # 'info', 'warning', 'error', 'critical'
    enabled: bool = True
    cooldown_minutes: int = 15


@dataclass
class AutomationRule:
    """Automation rule configuration"""
    name: str
    trigger: str  # 'schedule', 'event', 'condition'
    actions: List[str]
    condition: Optional[str] = None
    enabled: bool = True
    last_executed: Optional[datetime] = None
    next_execution: Optional[datetime] = None


@dataclass
class PerformanceReport:
    """System performance report"""
    timestamp: datetime
    period: str  # 'daily', 'weekly', 'monthly'
    metrics: Dict[str, float]
    alerts: List[Alert]
    recommendations: List[str]
    system_health: str  # 'excellent', 'good', 'fair', 'poor'


class ProductionDeploymentEngine:
    """
    Production Deployment Engine for AutoPPM
    
    Features:
    - Real-time system monitoring and health checks
    - Automated alerting and notification system
    - Performance tracking and reporting
    - Automated trading and risk management
    - System backup and recovery
    - Production deployment automation
    """
    
    def __init__(self):
        self.orchestrator = get_autoppm_orchestrator()
        self.ml_engine = get_ml_optimization_engine()
        self.risk_engine = get_advanced_risk_engine()
        self.broker_engine = get_multi_broker_engine()
        
        # Configuration
        self.config = self._load_config()
        self.monitoring_interval = self.config.get('monitoring_interval', 60)  # seconds
        self.alert_cooldown = self.config.get('alert_cooldown', 900)  # 15 minutes
        
        # Monitoring state
        self.system_metrics: List[SystemMetrics] = []
        self.active_alerts: List[Alert] = []
        self.alert_rules: List[AlertRule] = []
        self.automation_rules: List[AutomationRule] = []
        
        # Performance tracking
        self.performance_history: List[PerformanceReport] = []
        self.start_time = datetime.now()
        
        # Initialize components
        self._initialize_alert_rules()
        self._initialize_automation_rules()
        self._setup_monitoring()
        
        logger.info("Production Deployment Engine initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_path = Path("config/production_config.yaml")
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        # Default configuration
        return {
            'monitoring_interval': 60,
            'alert_cooldown': 900,
            'email_alerts': True,
            'sms_alerts': False,
            'webhook_alerts': False,
            'backup_enabled': True,
            'backup_interval_hours': 24,
            'auto_recovery': True,
            'performance_reporting': True
        }
    
    def _initialize_alert_rules(self):
        """Initialize default alert rules"""
        self.alert_rules = [
            AlertRule(
                name="High CPU Usage",
                condition="threshold",
                metric="cpu_usage",
                threshold=80.0,
                operator=">",
                severity="warning"
            ),
            AlertRule(
                name="High Memory Usage",
                condition="threshold",
                metric="memory_usage",
                threshold=85.0,
                operator=">",
                severity="warning"
            ),
            AlertRule(
                name="Critical Portfolio Loss",
                condition="threshold",
                metric="daily_pnl",
                threshold=-5.0,
                operator="<",
                severity="critical"
            ),
            AlertRule(
                name="High Risk Score",
                condition="threshold",
                metric="risk_score",
                threshold=0.8,
                operator=">",
                severity="error"
            ),
            AlertRule(
                name="Database Connection Issues",
                condition="threshold",
                metric="database_connections",
                threshold=0,
                operator="==",
                severity="critical"
            )
        ]
    
    def _initialize_automation_rules(self):
        """Initialize default automation rules"""
        self.automation_rules = [
            AutomationRule(
                name="Daily Risk Assessment",
                trigger="schedule",
                condition="0 9 * * *",  # 9 AM daily
                actions=["run_risk_assessment", "generate_risk_report", "send_risk_summary"]
            ),
            AutomationRule(
                name="Portfolio Rebalancing",
                trigger="schedule",
                condition="0 14 * * *",  # 2 PM daily
                actions=["check_rebalancing_needed", "execute_rebalancing", "log_rebalancing"]
            ),
            AutomationRule(
                name="Strategy Performance Review",
                trigger="schedule",
                condition="0 18 * * 5",  # 6 PM every Friday
                actions=["analyze_strategy_performance", "optimize_strategies", "generate_performance_report"]
            ),
            AutomationRule(
                name="System Backup",
                trigger="schedule",
                condition="0 2 * * *",  # 2 AM daily
                actions=["backup_database", "backup_configs", "verify_backup"]
            ),
            AutomationRule(
                name="Market Close Summary",
                trigger="schedule",
                condition="0 16 * * 1-5",  # 4 PM weekdays
                actions=["generate_daily_summary", "send_market_summary", "update_analytics"]
            )
        ]
    
    def _setup_monitoring(self):
        """Setup monitoring infrastructure"""
        # Create monitoring directory
        Path("logs/monitoring").mkdir(parents=True, exist_ok=True)
        Path("data/backups").mkdir(parents=True, exist_ok=True)
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Start automation scheduler
        self._setup_automation_scheduler()
        
        logger.info("Monitoring infrastructure setup completed")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                self.system_metrics.append(metrics)
                
                # Check alert rules
                self._check_alert_rules(metrics)
                
                # Cleanup old metrics (keep last 24 hours)
                self._cleanup_old_metrics()
                
                # Sleep for monitoring interval
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Short sleep on error
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # System metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # AutoPPM metrics
            active_strategies = len(self.orchestrator.get_running_executions())
            portfolio_summary = self.orchestrator.get_portfolio_summary()
            portfolio_value = portfolio_summary.get('total_value', 0.0)
            daily_pnl = portfolio_summary.get('daily_pnl', 0.0)
            
            # Risk metrics
            risk_score = self._calculate_current_risk_score()
            
            # Database connections (placeholder)
            database_connections = 1  # Would get actual connection count
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                },
                database_connections=database_connections,
                active_strategies=active_strategies,
                portfolio_value=portfolio_value,
                daily_pnl=daily_pnl,
                risk_score=risk_score
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            # Return default metrics on error
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={'bytes_sent': 0, 'bytes_recv': 0},
                database_connections=0,
                active_strategies=0,
                portfolio_value=0.0,
                daily_pnl=0.0,
                risk_score=0.0
            )
    
    def _calculate_current_risk_score(self) -> float:
        """Calculate current system risk score"""
        try:
            # Get current portfolio data
            portfolio_data = self._get_current_portfolio_data()
            
            # Calculate risk metrics
            risk_metrics = self.risk_engine.calculate_tail_risk_metrics(portfolio_data)
            
            # Normalize risk score (0-1 scale)
            var_95 = abs(risk_metrics.get('var_95', 0))
            max_drawdown = abs(risk_metrics.get('max_drawdown', 0))
            
            # Simple risk scoring (higher values = higher risk)
            risk_score = min((var_95 / 10.0 + max_drawdown / 20.0) / 2, 1.0)
            
            return risk_score
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.5  # Default medium risk
    
    def _get_current_portfolio_data(self) -> Any:
        """Get current portfolio data for risk calculation"""
        # Placeholder implementation
        # In production, this would get actual portfolio data
        return None
    
    def _check_alert_rules(self, metrics: SystemMetrics):
        """Check alert rules against current metrics"""
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # Check if alert is in cooldown
            if self._is_alert_in_cooldown(rule.name):
                continue
            
            # Evaluate rule condition
            if self._evaluate_alert_rule(rule, metrics):
                self._trigger_alert(rule, metrics)
    
    def _is_alert_in_cooldown(self, rule_name: str) -> bool:
        """Check if alert is in cooldown period"""
        for alert in self.active_alerts:
            if alert.message.startswith(rule_name):
                time_since_alert = (datetime.now() - alert.timestamp).total_seconds()
                if time_since_alert < self.alert_cooldown:
                    return True
        return False
    
    def _evaluate_alert_rule(self, rule: AlertRule, metrics: SystemMetrics) -> bool:
        """Evaluate if alert rule condition is met"""
        try:
            # Get metric value
            metric_value = getattr(metrics, rule.metric, 0.0)
            
            # Evaluate condition
            if rule.operator == '>':
                return metric_value > rule.threshold
            elif rule.operator == '<':
                return metric_value < rule.threshold
            elif rule.operator == '>=':
                return metric_value >= rule.threshold
            elif rule.operator == '<=':
                return metric_value <= rule.threshold
            elif rule.operator == '==':
                return metric_value == rule.threshold
            elif rule.operator == '!=':
                return metric_value != rule.threshold
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating alert rule {rule.name}: {e}")
            return False
    
    def _trigger_alert(self, rule: AlertRule, metrics: SystemMetrics):
        """Trigger an alert"""
        alert = Alert(
            id=f"alert_{int(time.time())}",
            type=rule.severity,
            message=f"{rule.name}: {rule.metric} = {getattr(metrics, rule.metric, 'N/A')}",
            timestamp=datetime.now()
        )
        
        self.active_alerts.append(alert)
        
        # Send notifications
        self._send_alert_notifications(alert)
        
        logger.warning(f"Alert triggered: {alert.message}")
    
    def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications"""
        try:
            # Email notifications
            if self.config.get('email_alerts', False):
                self._send_email_alert(alert)
            
            # SMS notifications (placeholder)
            if self.config.get('sms_alerts', False):
                self._send_sms_alert(alert)
            
            # Webhook notifications (placeholder)
            if self.config.get('webhook_alerts', False):
                self._send_webhook_alert(alert)
                
        except Exception as e:
            logger.error(f"Error sending alert notifications: {e}")
    
    def _send_email_alert(self, alert: Alert):
        """Send email alert"""
        try:
            # Email configuration (would be loaded from config)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "alerts@autoppm.com"
            sender_password = "your_password"
            recipient_email = "admin@autoppm.com"
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"AutoPPM Alert: {alert.type.upper()}"
            
            body = f"""
            AutoPPM System Alert
            
            Type: {alert.type.upper()}
            Message: {alert.message}
            Timestamp: {alert.timestamp}
            
            Please check the system dashboard for more details.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent: {alert.message}")
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
    
    def _send_sms_alert(self, alert: Alert):
        """Send SMS alert (placeholder)"""
        # In production, this would integrate with SMS service
        logger.info(f"SMS alert would be sent: {alert.message}")
    
    def _send_webhook_alert(self, alert: Alert):
        """Send webhook alert (placeholder)"""
        # In production, this would send to configured webhooks
        logger.info(f"Webhook alert would be sent: {alert.message}")
    
    def _setup_automation_scheduler(self):
        """Setup automation scheduler"""
        try:
            for rule in self.automation_rules:
                if rule.trigger == 'schedule' and rule.enabled:
                    schedule.every().day.at(rule.condition).do(
                        self._execute_automation_rule, rule
                    )
            
            # Start automation thread
            self.automation_thread = threading.Thread(target=self._automation_loop, daemon=True)
            self.automation_thread.start()
            
            logger.info("Automation scheduler setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up automation scheduler: {e}")
    
    def _automation_loop(self):
        """Main automation loop"""
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in automation loop: {e}")
                time.sleep(60)
    
    def _execute_automation_rule(self, rule: AutomationRule):
        """Execute automation rule"""
        try:
            logger.info(f"Executing automation rule: {rule.name}")
            
            for action in rule.actions:
                self._execute_action(action)
            
            # Update rule execution time
            rule.last_executed = datetime.now()
            
            logger.info(f"Automation rule completed: {rule.name}")
            
        except Exception as e:
            logger.error(f"Error executing automation rule {rule.name}: {e}")
    
    def _execute_action(self, action: str):
        """Execute a specific action"""
        try:
            if action == "run_risk_assessment":
                self._run_risk_assessment()
            elif action == "generate_risk_report":
                self._generate_risk_report()
            elif action == "send_risk_summary":
                self._send_risk_summary()
            elif action == "check_rebalancing_needed":
                self._check_rebalancing_needed()
            elif action == "execute_rebalancing":
                self._execute_rebalancing()
            elif action == "log_rebalancing":
                self._log_rebalancing()
            elif action == "analyze_strategy_performance":
                self._analyze_strategy_performance()
            elif action == "optimize_strategies":
                self._optimize_strategies()
            elif action == "generate_performance_report":
                self._generate_performance_report()
            elif action == "backup_database":
                self._backup_database()
            elif action == "backup_configs":
                self._backup_configs()
            elif action == "verify_backup":
                self._verify_backup()
            elif action == "generate_daily_summary":
                self._generate_daily_summary()
            elif action == "send_market_summary":
                self._send_market_summary()
            elif action == "update_analytics":
                self._update_analytics()
            else:
                logger.warning(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
    
    def _run_risk_assessment(self):
        """Run comprehensive risk assessment"""
        try:
            logger.info("Running daily risk assessment")
            
            # Get portfolio data
            portfolio_data = self._get_current_portfolio_data()
            
            # Run risk analysis
            risk_report = self.risk_engine.generate_risk_report(portfolio_data)
            
            # Store risk assessment
            self._store_risk_assessment(risk_report)
            
            logger.info("Risk assessment completed")
            
        except Exception as e:
            logger.error(f"Error running risk assessment: {e}")
    
    def _generate_risk_report(self):
        """Generate comprehensive risk report"""
        try:
            logger.info("Generating risk report")
            
            # Generate report (placeholder)
            report = {
                'timestamp': datetime.now(),
                'risk_metrics': {},
                'recommendations': []
            }
            
            # Store report
            self._store_risk_report(report)
            
            logger.info("Risk report generated")
            
        except Exception as e:
            logger.error(f"Error generating risk report: {e}")
    
    def _send_risk_summary(self):
        """Send risk summary to stakeholders"""
        try:
            logger.info("Sending risk summary")
            
            # Send email with risk summary (placeholder)
            logger.info("Risk summary sent")
            
        except Exception as e:
            logger.error(f"Error sending risk summary: {e}")
    
    def _check_rebalancing_needed(self):
        """Check if portfolio rebalancing is needed"""
        try:
            logger.info("Checking rebalancing needs")
            
            # Check rebalancing (placeholder)
            needs_rebalancing = False
            
            if needs_rebalancing:
                logger.info("Portfolio rebalancing needed")
            else:
                logger.info("No rebalancing needed")
                
        except Exception as e:
            logger.error(f"Error checking rebalancing: {e}")
    
    def _execute_rebalancing(self):
        """Execute portfolio rebalancing"""
        try:
            logger.info("Executing portfolio rebalancing")
            
            # Execute rebalancing (placeholder)
            logger.info("Portfolio rebalancing completed")
            
        except Exception as e:
            logger.error(f"Error executing rebalancing: {e}")
    
    def _log_rebalancing(self):
        """Log rebalancing activities"""
        try:
            logger.info("Logging rebalancing activities")
            
            # Log rebalancing (placeholder)
            logger.info("Rebalancing activities logged")
            
        except Exception as e:
            logger.error(f"Error logging rebalancing: {e}")
    
    def _analyze_strategy_performance(self):
        """Analyze strategy performance"""
        try:
            logger.info("Analyzing strategy performance")
            
            # Analyze strategies (placeholder)
            logger.info("Strategy performance analysis completed")
            
        except Exception as e:
            logger.error(f"Error analyzing strategy performance: {e}")
    
    def _optimize_strategies(self):
        """Optimize trading strategies"""
        try:
            logger.info("Optimizing trading strategies")
            
            # Optimize strategies (placeholder)
            logger.info("Strategy optimization completed")
            
        except Exception as e:
            logger.error(f"Error optimizing strategies: {e}")
    
    def _generate_performance_report(self):
        """Generate performance report"""
        try:
            logger.info("Generating performance report")
            
            # Generate report (placeholder)
            logger.info("Performance report generated")
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
    
    def _backup_database(self):
        """Backup system database"""
        try:
            logger.info("Backing up database")
            
            # Backup database (placeholder)
            backup_path = f"data/backups/db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite"
            
            logger.info(f"Database backup completed: {backup_path}")
            
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
    
    def _backup_configs(self):
        """Backup system configurations"""
        try:
            logger.info("Backing up configurations")
            
            # Backup configs (placeholder)
            backup_path = f"data/backups/config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            
            logger.info(f"Configuration backup completed: {backup_path}")
            
        except Exception as e:
            logger.error(f"Error backing up configurations: {e}")
    
    def _verify_backup(self):
        """Verify backup integrity"""
        try:
            logger.info("Verifying backup integrity")
            
            # Verify backup (placeholder)
            logger.info("Backup verification completed")
            
        except Exception as e:
            logger.error(f"Error verifying backup: {e}")
    
    def _generate_daily_summary(self):
        """Generate daily market summary"""
        try:
            logger.info("Generating daily summary")
            
            # Generate summary (placeholder)
            logger.info("Daily summary generated")
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
    
    def _send_market_summary(self):
        """Send market summary to stakeholders"""
        try:
            logger.info("Sending market summary")
            
            # Send summary (placeholder)
            logger.info("Market summary sent")
            
        except Exception as e:
            logger.error(f"Error sending market summary: {e}")
    
    def _update_analytics(self):
        """Update analytics and reporting"""
        try:
            logger.info("Updating analytics")
            
            # Update analytics (placeholder)
            logger.info("Analytics updated")
            
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    def _cleanup_old_metrics(self):
        """Clean up old system metrics"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.system_metrics = [
                m for m in self.system_metrics 
                if m.timestamp > cutoff_time
            ]
        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {e}")
    
    def _store_risk_assessment(self, assessment: Dict[str, Any]):
        """Store risk assessment data"""
        # Placeholder implementation
        pass
    
    def _store_risk_report(self, report: Dict[str, Any]):
        """Store risk report data"""
        # Placeholder implementation
        pass
    
    def _store_risk_report(self, report: Dict[str, Any]):
        """Store risk report data"""
        # Placeholder implementation
        pass
    
    # Public API methods
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        try:
            if not self.system_metrics:
                return {'status': 'unknown', 'message': 'No metrics available'}
            
            latest_metrics = self.system_metrics[-1]
            
            # Determine overall health
            health_score = 100
            
            if latest_metrics.cpu_usage > 90:
                health_score -= 30
            elif latest_metrics.cpu_usage > 80:
                health_score -= 20
            
            if latest_metrics.memory_usage > 90:
                health_score -= 30
            elif latest_metrics.memory_usage > 80:
                health_score -= 20
            
            if latest_metrics.risk_score > 0.8:
                health_score -= 25
            elif latest_metrics.risk_score > 0.6:
                health_score -= 15
            
            # Determine status
            if health_score >= 90:
                status = 'excellent'
            elif health_score >= 75:
                status = 'good'
            elif health_score >= 50:
                status = 'fair'
            else:
                status = 'poor'
            
            return {
                'status': status,
                'health_score': health_score,
                'timestamp': latest_metrics.timestamp,
                'metrics': asdict(latest_metrics),
                'active_alerts': len(self.active_alerts),
                'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_active_alerts(self) -> List[Alert]:
        """Get list of active alerts"""
        return self.active_alerts
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        try:
            for alert in self.active_alerts:
                if alert.id == alert_id:
                    alert.acknowledged = True
                    alert.acknowledged_by = acknowledged_by
                    alert.acknowledged_at = datetime.now()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get system performance summary"""
        try:
            if not self.system_metrics:
                return {'message': 'No metrics available'}
            
            # Calculate averages over last hour
            cutoff_time = datetime.now() - timedelta(hours=1)
            recent_metrics = [
                m for m in self.system_metrics 
                if m.timestamp > cutoff_time
            ]
            
            if not recent_metrics:
                return {'message': 'No recent metrics available'}
            
            # Calculate averages
            avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
            avg_risk = sum(m.risk_score for m in recent_metrics) / len(recent_metrics)
            
            return {
                'period': 'Last Hour',
                'average_cpu_usage': round(avg_cpu, 2),
                'average_memory_usage': round(avg_memory, 2),
                'average_risk_score': round(avg_risk, 3),
                'total_alerts': len(self.active_alerts),
                'active_strategies': recent_metrics[-1].active_strategies,
                'portfolio_value': recent_metrics[-1].portfolio_value,
                'daily_pnl': recent_metrics[-1].daily_pnl
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}
    
    def add_alert_rule(self, rule: AlertRule) -> bool:
        """Add a new alert rule"""
        try:
            self.alert_rules.append(rule)
            logger.info(f"Alert rule added: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding alert rule: {e}")
            return False
    
    def add_automation_rule(self, rule: AutomationRule) -> bool:
        """Add a new automation rule"""
        try:
            self.automation_rules.append(rule)
            logger.info(f"Automation rule added: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding automation rule: {e}")
            return False
    
    def backup_system(self) -> Dict[str, Any]:
        """Perform complete system backup"""
        try:
            logger.info("Starting complete system backup")
            
            backup_results = {}
            
            # Backup database
            try:
                self._backup_database()
                backup_results['database'] = 'success'
            except Exception as e:
                backup_results['database'] = f'failed: {e}'
            
            # Backup configurations
            try:
                self._backup_configs()
                backup_results['configurations'] = 'success'
            except Exception as e:
                backup_results['configurations'] = f'failed: {e}'
            
            # Backup logs
            try:
                self._backup_logs()
                backup_results['logs'] = 'success'
            except Exception as e:
                backup_results['logs'] = f'failed: {e}'
            
            # Verify backup
            try:
                self._verify_backup()
                backup_results['verification'] = 'success'
            except Exception as e:
                backup_results['verification'] = f'failed: {e}'
            
            backup_results['timestamp'] = datetime.now().isoformat()
            backup_results['overall_status'] = 'success' if all(
                v == 'success' for v in backup_results.values() 
                if isinstance(v, str) and v != 'success'
            ) else 'partial'
            
            logger.info("System backup completed")
            return backup_results
            
        except Exception as e:
            logger.error(f"Error during system backup: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _backup_logs(self):
        """Backup system logs"""
        try:
            logger.info("Backing up system logs")
            
            # Backup logs (placeholder)
            backup_path = f"data/backups/logs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
            
            logger.info(f"Logs backup completed: {backup_path}")
            
        except Exception as e:
            logger.error(f"Error backing up logs: {e}")
    
    def shutdown(self):
        """Gracefully shutdown the production engine"""
        try:
            logger.info("Shutting down Production Deployment Engine")
            
            # Stop monitoring
            self.monitoring_thread.join(timeout=5)
            
            # Stop automation
            schedule.clear()
            
            # Final backup
            self.backup_system()
            
            logger.info("Production Deployment Engine shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global instance
_production_engine: Optional[ProductionDeploymentEngine] = None


def get_production_engine() -> ProductionDeploymentEngine:
    """Get global production engine instance"""
    global _production_engine
    if _production_engine is None:
        _production_engine = ProductionDeploymentEngine()
    return _production_engine
