from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from database import SessionLocal
from models import BookDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_old_books():
    """
    Удаляет книги, добавленные более 30 дней назад.
    Для тестирования можно изменить интервал (например, на 1 минуту).
    """
    db: Session = SessionLocal()
    try:
        cutoff_date = datetime.now() - timedelta(days=30)
        deleted_count = db.query(BookDB).filter(
            BookDB.created_at < cutoff_date
        ).delete(synchronize_session=False)
        db.commit()
        if deleted_count:
            logger.info(f"Удалено старых книг: {deleted_count}")
        else:
            logger.info("Нет старых книг для удаления.")
    except Exception as e:
        logger.error(f"Ошибка при удалении старых книг: {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    """Запускает планировщик задач."""
    scheduler = BackgroundScheduler()
    # Выполнять каждый день в 3:00
    trigger = CronTrigger(hour=3, minute=0)
    scheduler.add_job(delete_old_books, trigger, id="cleanup_old_books")
    scheduler.start()
    logger.info("Планировщик запущен. Задача 'cleanup_old_books' запланирована на 3:00 каждый день.")
    return scheduler