from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import College, Base, CourseName, User

engine = create_engine('sqlite:///colleges.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Rupesh sai", email="15pa1a0446@vishnu.edu.in",
             picture='https://bit.ly/2LL8M1h')
session.add(User1)
session.commit()

# courses for SRKR college
college1 = College(user_id=1, name="SRKR engineering college")

session.add(college1)
session.commit()

course1 = CourseName(user_id=1, name="ECE",
                     description="Electronics and Communication Engineering",
                     fee="$1000", college=college1)

session.add(course1)
session.commit()


course2 = CourseName(user_id=1, name="CSE",
                     description="Computer Science Engineering",
                     fee="$1100", college=college1)

session.add(course2)
session.commit()


course3 = CourseName(user_id=1, name="EEE",
                     description="Electrical and Electronics Engineering",
                     fee="$900", college=college1)

session.add(course3)
session.commit()


course4 = CourseName(user_id=1, name="ME",
                     description="Mechanical Engineering",
                     fee="$1000", college=college1)

session.add(course4)
session.commit()


course5 = CourseName(user_id=1, name="IT",
                     description="Information Technology",
                     fee="$1000", college=college1)

session.add(course5)
session.commit()

# Courses  for VIT college
college2 = College(user_id=1, name="Vishnu Institute Of Technology")


session.add(college2)
session.commit()


course1 = CourseName(user_id=1, name="ECE",
                     description="Electronics and Communication Engineering",
                     fee="$1000", college=college2)

session.add(course1)
session.commit()


course2 = CourseName(user_id=1, name="CSE",
                     description="Computer Science Engineering",
                     fee="$1200", college=college2)

session.add(course2)
session.commit()


course3 = CourseName(user_id=1, name="EEE",
                     description="Electrical and Electronics Engineering",
                     fee="$600", college=college2)

session.add(course3)
session.commit()


course4 = CourseName(user_id=1, name="ME",
                     description="Mechanical Engineering",
                     fee="$1000", college=college2)

session.add(course4)
session.commit()


course5 = CourseName(user_id=1, name="IT",
                     description="Information Technology",
                     fee="$1200", college=college2)

session.add(course5)
session.commit()


course6 = CourseName(user_id=1, name="CE", description="Civil Engineering",
                     fee="$1000", college=college2)

session.add(course6)
session.commit()


# Courses  for SCET college
college3 = College(user_id=1,
                   name="Swarnandra College of Engineering and Technology")


session.add(college3)
session.commit()


course1 = CourseName(user_id=1, name="ECE",
                     description="Electronics and Communication Engineering",
                     fee="$800", college=college3)

session.add(course1)
session.commit()


course2 = CourseName(user_id=1, name="CSE",
                     description="Computer Science Engineering",
                     fee="$1000", college=college3)

session.add(course2)
session.commit()


course3 = CourseName(user_id=1, name="EEE",
                     description="Electrical and Electronics Engineering",
                     fee="$600", college=college3)

session.add(course3)
session.commit()


course4 = CourseName(user_id=1, name="ME",
                     description="Mechanical Engineering",
                     fee="$800", college=college3)

session.add(course4)
session.commit()


course5 = CourseName(user_id=1, name="CE", description="Civil Engineering",
                     fee="$1000", college=college3)

session.add(course5)
session.commit()


# Courses  for GVIT college
college4 = College(user_id=1,
                   name="Grandhi Varalakshmi Institute of Technology")


session.add(college4)
session.commit()


course1 = CourseName(user_id=1, name="ECE",
                     description="Electronics and Communication Engineering",
                     fee="$800", college=college4)

session.add(course1)
session.commit()


course2 = CourseName(user_id=1, name="CSE",
                     description="Computer Science Engineering",
                     fee="$1000", college=college4)

session.add(course2)
session.commit()


course3 = CourseName(user_id=1, name="EEE",
                     description="Electrical and Electronics Engineering",
                     fee="$600", college=college4)

session.add(course3)
session.commit()


course4 = CourseName(user_id=1, name="ME",
                     description="Mechanical Engineering",
                     fee="$800", college=college4)

session.add(course4)
session.commit()


course5 = CourseName(user_id=1, name="IT",
                     description="Information Technology",
                     fee="$1000", college=college4)

session.add(course5)
session.commit()


# Courses  for BIET college
college5 = College(user_id=1,
                   name="Bhimavaram Institute of Engineering and Technology")


session.add(college5)
session.commit()


course1 = CourseName(user_id=1, name="ECE",
                     description="Electronics and Communication Engineering",
                     fee="$800", college=college5)

session.add(course1)
session.commit()


course2 = CourseName(user_id=1, name="CSE",
                     description="Computer Science Engineering",
                     fee="$1000", college=college5)

session.add(course2)
session.commit()


course3 = CourseName(user_id=1, name="IT",
                     description="Informatoion Technology",
                     fee="$1000", college=college5)

session.add(course3)
session.commit()


course4 = CourseName(user_id=1, name="ME",
                     description="Mechanical Engineering",
                     fee="$800", college=college5)

session.add(course4)
session.commit()


course5 = CourseName(user_id=1, name="CE", description="Civil Engineering",
                     fee="$1000", college=college5)

session.add(course5)
session.commit()
print "added menu items!"

