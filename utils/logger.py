"""
Enhanced Logging System for Agent Task Management

Provides comprehensive logging with:
- Multiple log levels and handlers
- Disk persistence with rotation
- Structured JSON logging for audit trails
- Performance monitoring
- Configurable output formats
- Emoji-enhanced UX for better accessibility and visual recognition
"""

import logging
import logging.config
import logging.handlers
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from contextlib import contextmanager

try:
    from pythonjsonlogger import jsonlogger
except ImportError:
    # Fallback if python-json-logger not available
    jsonlogger = None

# Emoji mapping for enhanced UX and accessibility
LOG_EMOJIS = {
    'DEBUG': '🔍',      # Magnifying glass - investigation/debugging
    'INFO': '📝',       # Memo - information/documentation
    'WARNING': '⚠️',    # Warning sign - caution/attention needed
    'ERROR': '❌',      # Cross mark - error/failure
    'CRITICAL': '🚨',   # Rotating light - urgent/critical
    
    # Operation-specific emojis
    'SYSTEM_INIT': '🚀',     # Rocket - system startup
    'TASK_CREATE': '✨',     # Sparkles - new creation
    'TASK_UPDATE': '🔄',     # Counterclockwise arrows - update/refresh
    'TASK_COMPLETE': '✅',   # Check mark - completion/success
    'TASK_DELETE': '🗑️',    # Wastebasket - deletion
    'SYNC_START': '🔗',      # Link - synchronization start
    'SYNC_SUCCESS': '✅',    # Check mark - sync success
    'SYNC_CONFLICT': '⚡',   # Lightning - conflict/attention
    'PERFORMANCE': '⚡',     # Lightning - performance/speed
    'SECURITY': '🔒',       # Lock - security/auth
    'NETWORK': '🌐',        # Globe - network operations
    'DATABASE': '💾',       # Floppy disk - data operations
    'VALIDATION': '🔍',     # Magnifying glass - validation/checking
    'AUTO_FIX': '🔧',       # Wrench - fixing/repair
    'EXPORT': '📤',         # Outbox tray - export/send
    'IMPORT': '📥',         # Inbox tray - import/receive
    'BACKUP': '💾',         # Floppy disk - backup/save
    'CLEANUP': '🧹',        # Broom - cleanup/maintenance
}

def get_emoji_for_level(level: str) -> str:
    """Get emoji for log level with fallback"""
    return LOG_EMOJIS.get(level.upper(), '📝')

def get_emoji_for_operation(operation: str) -> str:
    """Get emoji for specific operation"""
    return LOG_EMOJIS.get(operation.upper(), '🔧')

class EmojiFormatter(logging.Formatter):
    """Enhanced formatter with emoji support for better UX"""
    
    def format(self, record):
        # Add emoji based on level or operation
        if hasattr(record, 'operation'):
            emoji = get_emoji_for_operation(record.operation)
        else:
            emoji = get_emoji_for_level(record.levelname)
        
        # Add emoji to the message
        original_msg = record.getMessage()
        if not original_msg.startswith(tuple(LOG_EMOJIS.values())):
            record.msg = f"{emoji} {original_msg}"
            record.args = ()  # Clear args since we've already formatted the message
        
        return super().format(record)

class EnhancedLogger(logging.Logger):
    """Enhanced logger with emoji support and semantic methods"""
    
    def __init__(self, name):
        super().__init__(name)
        self.emoji_enabled = True
    
    def log_operation(self, level: int, operation: str, message: str, *args, **kwargs):
        """Log with operation-specific emoji"""
        extra = kwargs.get('extra', {})
        extra['operation'] = operation
        kwargs['extra'] = extra
        self.log(level, message, *args, **kwargs)
    
    def system_init(self, message: str, *args, **kwargs):
        """Log system initialization with rocket emoji"""
        self.log_operation(logging.INFO, 'SYSTEM_INIT', message, *args, **kwargs)
    
    def task_created(self, message: str, *args, **kwargs):
        """Log task creation with sparkles emoji"""
        self.log_operation(logging.INFO, 'TASK_CREATE', message, *args, **kwargs)
    
    def task_updated(self, message: str, *args, **kwargs):
        """Log task update with refresh emoji"""
        self.log_operation(logging.INFO, 'TASK_UPDATE', message, *args, **kwargs)
    
    def task_completed(self, message: str, *args, **kwargs):
        """Log task completion with check mark emoji"""
        self.log_operation(logging.INFO, 'TASK_COMPLETE', message, *args, **kwargs)
    
    def performance_log(self, message: str, *args, **kwargs):
        """Log performance with lightning emoji"""
        self.log_operation(logging.INFO, 'PERFORMANCE', message, *args, **kwargs)
    
    def sync_operation(self, message: str, *args, **kwargs):
        """Log sync operations with link emoji"""
        self.log_operation(logging.INFO, 'SYNC_START', message, *args, **kwargs)
    
    def validation_log(self, message: str, *args, **kwargs):
        """Log validation with magnifying glass emoji"""
        self.log_operation(logging.INFO, 'VALIDATION', message, *args, **kwargs)
    
    def auto_fix_log(self, message: str, *args, **kwargs):
        """Log auto-fix operations with wrench emoji"""
        self.log_operation(logging.INFO, 'AUTO_FIX', message, *args, **kwargs)

# Global configuration for logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "simple": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",  
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "emoji": {
            "format": "%(asctime)s %(emoji)s %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter" if jsonlogger else "logging.Formatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(funcName)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "emoji",
            "stream": "ext://sys.stdout"
        },
        "console_simple": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple", 
            "stream": "ext://sys.stdout"
        },
        "file_debug": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/agent_tasks_debug.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        },
        "file_info": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO", 
            "formatter": "simple",
            "filename": "logs/agent_tasks.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
            "encoding": "utf8"
        },
        "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed", 
            "filename": "logs/agent_tasks_errors.log",
            "maxBytes": 5242880,  # 5MB
            "backupCount": 10,
            "encoding": "utf8"
        },
        "audit": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "json" if jsonlogger else "detailed",
            "filename": "logs/audit.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "encoding": "utf8"
        },
        "performance": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json" if jsonlogger else "detailed",
            "filename": "logs/performance.log", 
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        }
    },
    "loggers": {
        "agent_task_management": {
            "level": "DEBUG",
            "handlers": ["console", "file_debug", "file_info", "file_error"],
            "propagate": False
        },
        "agent_task_management.audit": {
            "level": "INFO",
            "handlers": ["audit"],
            "propagate": False
        },
        "agent_task_management.performance": {
            "level": "INFO", 
            "handlers": ["performance"],
            "propagate": False
        }
    }
}


class AuditLogger:
    """Specialized logger for audit events and compliance tracking"""
    
    def __init__(self):
        self.logger = logging.getLogger("agent_task_management.audit")
        
    def log_task_operation(self, operation: str, task_id: str, agent: str, 
                          user: str = None, details: Dict = None):
        """Log task operations for audit trail"""
        audit_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "task_id": task_id,
            "agent": agent,
            "user": user or "system",
            "details": details or {}
        }
        
        if jsonlogger:
            self.logger.info("", extra=audit_data)
        else:
            self.logger.info(json.dumps(audit_data))
    
    def log_system_event(self, event_type: str, description: str, 
                        metadata: Dict = None):
        """Log system-level events"""
        event_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description,
            "metadata": metadata or {}
        }
        
        if jsonlogger:
            self.logger.info("", extra=event_data)
        else:
            self.logger.info(json.dumps(event_data))


class PerformanceLogger:
    """Specialized logger for performance metrics and timing"""
    
    def __init__(self):
        self.logger = logging.getLogger("agent_task_management.performance")
    
    def log_operation_timing(self, operation: str, duration: float, 
                           context: Dict = None):
        """Log operation timing data"""
        perf_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "context": context or {}
        }
        
        if jsonlogger:
            self.logger.info("", extra=perf_data)
        else:
            self.logger.info(json.dumps(perf_data))
    
    def log_cache_stats(self, cache_name: str, hits: int, misses: int, 
                       hit_rate: float, context: Dict = None):
        """Log cache performance statistics"""
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "cache_name": cache_name,
            "hits": hits,
            "misses": misses,
            "hit_rate": round(hit_rate, 3),
            "context": context or {}
        }
        
        if jsonlogger:
            self.logger.info("", extra=cache_data)
        else:
            self.logger.info(json.dumps(cache_data))


@contextmanager
def log_performance(operation: str, logger_instance=None, context: Dict = None):
    """Context manager for timing operations"""
    start_time = time.time()
    perf_logger = logger_instance or PerformanceLogger()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        perf_logger.log_operation_timing(operation, duration, context)


def ensure_log_directory():
    """Ensure logs directory exists"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


def setup_logging(config_path: Optional[str] = None, 
                 log_level: str = "INFO",
                 console_only: bool = False,
                 enable_emoji: bool = True) -> Dict[str, Any]:
    """
    Set up comprehensive logging system with emoji support
    
    Args:
        config_path: Path to custom logging configuration file
        log_level: Default log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_only: If True, only log to console (useful for testing)
        enable_emoji: If True, use emoji-enhanced logging for better UX
    
    Returns:
        Dictionary of configured loggers and utilities
    """
    # Register custom formatter and logger classes
    logging.setLoggerClass(EnhancedLogger)
    
    # Ensure logs directory exists
    ensure_log_directory()
    
    # Load configuration
    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            config = json.load(f)
    else:
        config = LOGGING_CONFIG.copy()
    
    # Modify config for console-only mode
    if console_only:
        # Remove file handlers
        for logger_config in config["loggers"].values():
            logger_config["handlers"] = ["console"]
    
    # Override log level if specified
    if log_level:
        for logger_config in config["loggers"].values():
            logger_config["level"] = log_level.upper()
    
    # Apply configuration
    try:
        logging.config.dictConfig(config)
    except Exception as e:
        # Fallback to basic logging if configuration fails
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        print(f"Warning: Failed to configure advanced logging, using basic setup: {e}")
    
    # Get main logger and enhance with emoji if enabled
    main_logger = logging.getLogger("agent_task_management")
    
    if enable_emoji:
        # Apply emoji formatter to console handlers
        for handler in main_logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                emoji_formatter = EmojiFormatter(
                    fmt="%(asctime)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
                handler.setFormatter(emoji_formatter)
    
    # Return configured loggers and utilities
    return {
        "main": main_logger,
        "audit": AuditLogger(),
        "performance": PerformanceLogger(),
        "log_performance": log_performance,
        "emoji_enabled": enable_emoji
    }


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (optional, defaults to agent_task_management)
    
    Returns:
        Logger instance
    """
    logger_name = name or "agent_task_management"
    return logging.getLogger(logger_name)


# Initialize default loggers
try:
    _loggers = setup_logging()
    logger = _loggers["main"]
    audit_logger = _loggers["audit"]
    performance_logger = _loggers["performance"]
except Exception as e:
    # Fallback to basic logger if setup fails
    logger = logging.getLogger("agent_task_management")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    audit_logger = None
    performance_logger = None
    print(f"Warning: Using fallback logging setup: {e}")


# Convenience methods for different log levels  
def debug(message: str, *args, **kwargs):
    """Log a debug message."""
    logger.debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs):
    """Log an info message."""
    logger.info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """Log a warning message."""
    logger.warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """Log an error message."""
    logger.error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs):
    """Log a critical message."""
    logger.critical(message, *args, **kwargs)


# Export commonly used items
__all__ = [
    'logger',
    'audit_logger', 
    'performance_logger',
    'setup_logging',
    'get_logger',
    'log_performance',
    'AuditLogger',
    'PerformanceLogger',
    'debug',
    'info',
    'warning', 
    'error',
    'critical'
]