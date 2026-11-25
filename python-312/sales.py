"""Monthly sales chart generator.

Supported boundary contract:
  - Interior valid inputs: calendar.JANUARY (1) through calendar.OCTOBER (10)
  - Supported absent boundary: calendar.NOVEMBER (11) and calendar.DECEMBER (12)
    are absent from the sales mapping and intentionally produce no visual output
  - Domain range: min sale = 5 (Jan), max sale = 23 (Oct)
"""
import calendar

sales = {
    calendar.JANUARY: 5,
    calendar.FEBRUARY: 9,
    calendar.MARCH: 6,
    calendar.APRIL: 14,
    calendar.MAY: 9,
    calendar.JUNE: 8,
    calendar.JULY: 15,
    calendar.AUGUST: 22,
    calendar.SEPTEMBER: 20,
    calendar.OCTOBER: 23,
}
for month in calendar.Month:
    if month in sales:
        print(
            f"{month.value:2d} {month.name:<10} {sales[month]:2d} {'*' * sales[month]}"
        )
