import os
class Config:
  SECRET_KEY = '880f3d9998b29afbe5fba58f83d2c598'
  SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
  SG_KEY = os.environ.get('SENDGRID_API_KEY')