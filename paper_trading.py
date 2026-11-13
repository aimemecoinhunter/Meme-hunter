
class PaperTrading:
    """Simulator only. Does not connect to a wallet or execute real trades."""

    LADDER = [
        (0.30, 0.20),
        (0.60, 0.20),
        (1.00, 0.15),
        (2.00, 0.15),
    ]

    def __init__(self, capital=1000, max_position=200, max_open=5):
        self.initial_capital = float(capital)
        self.available_capital = float(capital)
        self.max_position = float(max_position)
        self.max_open = int(max_open)
        self.positions = {}
        self.moonbags = []
        self.profit_balance = 0.0
        self.events = []

    def buy(self, token, price, amount=200):
        if price <= 0 or amount <= 0:
            return "Invalid price or amount."

        if token in self.positions:
            return "This token already has an open position."

        if len(self.positions) >= self.max_open:
            return "Maximum 5 open positions reached."

        if amount > self.max_position:
            return "Amount exceeds the per-position limit."

        if amount > self.available_capital:
            return "Not enough available capital."

        quantity = amount / price

        self.available_capital -= amount
        self.positions[token] = {
            "entry_price": float(price),
            "initial_quantity": quantity,
            "remaining_quantity": quantity,
            "cost": float(amount),
            "principal_returned": 0.0,
            "sold_levels": []
        }

        self.events.append(
            f"BUY {token}: {amount:.2f} USDC"
        )
        return f"Simulated purchase: {quantity:.6f} {token}"

    def update_price(self, token, price):
        if token not in self.positions:
            return ["No open position for this token."]

        if price <= 0:
            return ["Invalid price."]

        position = self.positions[token]
        entry = position["entry_price"]
        initial_qty = position["initial_quantity"]
        messages = []

        for level, fraction in self.LADDER:
            if level in position["sold_levels"]:
                continue

            target_price = entry * (1 + level)

            if price >= target_price:
                quantity = initial_qty * fraction
                proceeds = quantity * target_price

                # Return original capital first.
                unrecovered = (
                    position["cost"]
                    - position["principal_returned"]
                )
                principal_part = min(proceeds, unrecovered)
                profit_part = proceeds - principal_part

                self.available_capital += principal_part
                self.profit_balance += profit_part
                position["principal_returned"] += principal_part
                position["remaining_quantity"] -= quantity
                position["sold_levels"].append(level)

                message = (
                    f"SELL +{level * 100:.0f}%: "
                    f"{fraction * 100:.0f}% of initial quantity. "
                    f"Proceeds: {proceeds:.2f} USDC"
                )
                messages.append(message)
                self.events.append(message)

        # After all four sales, separate the 30% Moonbag.
        if len(position["sold_levels"]) == 4:
            moonbag_qty = initial_qty * 0.30

            self.moonbags.append({
                "token": token,
                "quantity": moonbag_qty,
                "entry_price": entry
            })

            messages.append(
                f"MOONBAG saved: {moonbag_qty:.6f} {token}. "
                "No automatic sale."
            )

            self.events.append(f"MOONBAG saved: {token}")
            del self.positions[token]

        if not messages:
            messages.append("No profit target reached yet.")

        return messages

    def status(self):
        return {
            "initial_capital": self.initial_capital,
            "available_capital": round(self.available_capital, 2),
            "profit_balance": round(self.profit_balance, 2),
            "open_positions": len(self.positions),
            "moonbags": len(self.moonbags),
            "events": self.events
        }
        
