from datetime import datetime
from unittest import TestCase

from ui.HtmlMessageView import HtmlMessageView


class HtmlMessageViewTests(TestCase):

	current = datetime(2023, 12, 29, 19, 34, 15)

	def testTodayFormat(self):
		other = datetime(2023, 12, 29, 14, 52, 30)
		result = HtmlMessageView.formatDateTime(self.current, other)
		self.assertEqual(result, '<p>14:52:30</p>')

	def testPastWeekFormat(self):
		other = datetime(2023, 12, 27, 14, 52, 30)
		result = HtmlMessageView.formatDateTime(self.current, other)
		self.assertEqual(result, '<p>Wednesday</p><p>14:52:30</p>')

	def testThisMonthFormat(self):
		other = datetime(2023, 12, 6, 14, 52, 30)
		result = HtmlMessageView.formatDateTime(self.current, other)
		self.assertEqual(result, '<p> 6 Dec</p><p>14:52:30</p>')  # Note: Leading space for single-digit day
		other = datetime(2023, 12, 18, 14, 52, 30)
		result = HtmlMessageView.formatDateTime(self.current, other)
		self.assertEqual(result, '<p>18 Dec</p><p>14:52:30</p>')

	def testFullDateFormat(self):
		other = datetime(2021, 5, 9, 15, 53, 31)
		result = HtmlMessageView.formatDateTime(self.current, other)
		self.assertEqual(result, '<p>2021-05-09</p><p>15:53:31</p>')