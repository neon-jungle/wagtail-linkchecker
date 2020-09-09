import re
from wagtail import __version__ as WAGTAIL_VERSION


def is_wagtail_version_more_than_equal_to_2_5():
	expression = '^((2.([5-9]{1,}|([1-9]{1,}[0-9]{1,}))(.\d+)*)|(([3-9]{1,})(.\d+)*))$'

	return re.search(expression, WAGTAIL_VERSION)


def is_wagtail_version_more_than_equal_to_2_0():
	expression = '^((2.([0-9]{1,}|([1-9]{1,}[0-9]{1,}))(.\d+)*)|(([3-9]{1,})(.\d+)*))$'

	return re.search(expression, WAGTAIL_VERSION)

