class User:
    id: int
    date_added: str
    name: str
    cash: int
    commission: int
    available_bundles: str

    def __init__(self, id, date_added, name, cash, commission, available_bundles):
        self.id = id
        self.date_added = date_added
        self.name = name
        self.cash = cash
        self.commission = commission
        self.available_bundles = available_bundles


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


    def __init__(self, bundle_id, created_date, author_id, name, price, company, date_interview, direction, assembling,bought_count,earned):
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