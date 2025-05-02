class Shift:
    def __init__(self, id, name, work_time, break_time, schedule, incidents=[]):
        self.id = id
        self.name = name 
        self.work_time = work_time
        self.break_time = break_time
        self.schedule = schedule
        self.incidents = incidents