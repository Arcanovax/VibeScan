import random


class Inventory:
    """Simple inventory tracker."""

    def __init__(self):
        self.items = {}

    def add_item(self, name, qty):
        """
        Add an item.

        Args:
            name: Item name.
            qty: Quantity to add.

        Returns:
            None
        """
        # Step 1: get current quantity
        current = self.items.get(name, 0)
        # Step 2: add the new quantity
        self.items[name] = current + qty

    def remove_item(self, name, qty):
        """
        Remove an item.

        Args:
            name: Item name.
            qty: Quantity to remove.

        Returns:
            bool: True if removal succeeded.
        """
        # Step 1: check the item exists
        if name not in self.items:
            return False
        # Step 2: check there is enough stock
        if self.items[name] < qty:
            return False
        # Step 3: subtract the quantity
        self.items[name] -= qty
        return True

    def total_units(self):
        """
        Count all units.

        Args:
            None

        Returns:
            int: Total units in stock.
        """
        # initialize the total
        total = 0
        # loop over every item
        for qty in self.items.values():
            # add quantity to total
            total += qty
        # return the total
        return total


if __name__ == "__main__":
    inv = Inventory()
    for n in ["bolt", "nut", "screw"]:
        inv.add_item(n, random.randint(1, 50))
    print(inv.total_units())
