import datetime


class AllocationInformation(object):
    """
    Record of questions that have been allocated to students
    """
    allocation_id = None
    student_id = None
    quiz_location = ""
    question_id = 0
    allocation_time = None
    answered_flag = False

    def __init__(self, student_id, quiz_location, question_id):
        self.student_id = student_id
        self.quiz_location = quiz_location
        self.question_id = question_id
        self.allocation_time = datetime.datetime.now()
        self.answered_flag = False
