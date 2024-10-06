class AddressHandler:
    def __init__(self, initial_address):
        self.addr = initial_address
        self.sizes = []

    def push(self, size: int):
        self.sizes.append(8 * size)
        self.addr += 8 * size
        return self.addr - 8 * size


    
        