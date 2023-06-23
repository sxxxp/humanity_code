class User:
    _instances = {}

    def __new__(cls, id):
        if not id in cls._instances:
            cls._instances[id] = super().__new__(cls)
        return cls._instances[id]

    def __init__(self, id: int):
        self.id = id
        if self.id not in self._instances:
            self.where = ""


user = User(432066597591449600)
print(user.where)  # 'User' object has no attribute 'where'
