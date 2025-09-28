"""
Setting model for Rafad Clinic System
"""
from . import db


class Setting(db.Model):
    """Setting model for storing system configuration"""
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    setting_name = db.Column(db.String(64), unique=True, nullable=False)
    setting_value = db.Column(db.String(256))
    setting_type = db.Column(db.String(20), default='string')  # string, integer, boolean, json
    description = db.Column(db.String(256))
    is_public = db.Column(db.Boolean, default=True)  # Whether visible to non-admin users
    
    @classmethod
    def get_value(cls, name, default=None):
        """Get setting value by name"""
        setting = cls.query.filter_by(setting_name=name).first()
        if not setting:
            return default
        
        # Convert value based on type
        if setting.setting_type == 'integer':
            return int(setting.setting_value)
        elif setting.setting_type == 'boolean':
            return setting.setting_value.lower() in ('true', '1', 'yes')
        elif setting.setting_type == 'json':
            import json
            return json.loads(setting.setting_value)
        else:
            return setting.setting_value
    
    @classmethod
    def set_value(cls, name, value, setting_type='string', description=None, is_public=True):
        """Set setting value by name"""
        # Convert value based on type
        if setting_type == 'boolean':
            value = str(value).lower()
        elif setting_type == 'json':
            import json
            value = json.dumps(value)
        else:
            value = str(value)
            
        setting = cls.query.filter_by(setting_name=name).first()
        if setting:
            setting.setting_value = value
            if description:
                setting.description = description
            setting.is_public = is_public
        else:
            setting = cls(
                setting_name=name,
                setting_value=value,
                setting_type=setting_type,
                description=description,
                is_public=is_public
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting
    
    def __repr__(self):
        return f'<Setting {self.setting_name}: {self.setting_value}>'