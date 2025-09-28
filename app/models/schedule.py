"""
Schedule model for Rafad Clinic System
"""
from . import db


class Schedule(db.Model):
    """Schedule model for storing doctor's availability"""
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    break_start = db.Column(db.Time)  # Optional break time
    break_end = db.Column(db.Time)
    
    @property
    def day_name(self):
        """Return name of day of week"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[self.day_of_week]
    
    @property
    def time_slot(self):
        """Return formatted time slot"""
        start = self.start_time.strftime("%H:%M")
        end = self.end_time.strftime("%H:%M")
        return f"{start} - {end}"
    
    def __repr__(self):
        return f'<Schedule {self.doctor.full_name if self.doctor else "Unknown"}: {self.day_name} {self.time_slot}>'