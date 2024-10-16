class User:
    id: int
    date_added: str
    name: str
    cash: int
    commission: int
    available_bundles: str
    job_title: str
    last_action: str

    def __init__(self, id, date_added, name, cash, commission, available_bundles,job_title,last_action):
        self.id = id
        self.date_added = date_added
        self.name = name
        self.cash = cash
        self.commission = commission
        self.available_bundles = available_bundles
        self.job_title = job_title
        self.last_action = last_action


class Bundle:
    bundle_id: int
    created_date: str
    author_id: int
    name: str
    price: int
    company: str
    date_interview: str
    direction: str
    assembling: list
    bought_count: int
    earned: int

    def __init__(self, bundle_id, created_date, author_id, name, price, company, date_interview, direction, assembling,
                 bought_count, earned):
        self.bundle_id = bundle_id
        self.created_date = created_date
        self.author_id = author_id
        self.name = name
        self.price = price
        self.company = company
        self.date_interview = date_interview
        self.direction = direction
        self.assembling = assembling
        self.bought_count = bought_count
        self.earned = earned


class MoneyRequest:
    id: int
    user_id: int
    for_author: int
    commission: int
    ndfl: int
    request_date: str
    created_date: str

    def __init__(self, id, user_id, for_author, commission, ndfl, request_date, created_date):
        self.id = id
        self.user_id = user_id
        self.for_author = for_author
        self.commission = commission
        self.ndfl = ndfl
        self.request_date = request_date
        self.created_date = created_date
