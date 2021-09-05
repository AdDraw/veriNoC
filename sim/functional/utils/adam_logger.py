import git
import logging
import sys
from logging.handlers import RotatingFileHandler
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s — %(message)s")
LOG_FILE = "sim.log"


def get_git_root(path):
  git_repo = git.Repo(path, search_parent_directories=True)
  git_root_t = git_repo.git.rev_parse("--show-toplevel")
  return git_root_t


def get_console_handler():
  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setFormatter(FORMATTER)
  return console_handler


def get_file_handler(log_file=LOG_FILE):
  file_handler = RotatingFileHandler(log_file, mode='w', backupCount=6)
  file_handler.setFormatter(FORMATTER)
  return file_handler


def get_logger(logger_name, log_lvl):
  logger = logging.getLogger(logger_name)
  if log_lvl:
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
  else:
    logger.setLevel(logging.INFO)
  logger.addHandler(get_console_handler())
  logger.addHandler(get_file_handler())
  logger.propagate = False
  return logger
