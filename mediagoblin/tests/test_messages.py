# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011 Free Software Foundation, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mediagoblin.messages import fetch_messages, add_message
from mediagoblin.tests.tools import setup_fresh_app
from mediagoblin import util


@setup_fresh_app
def test_messages(test_app):
    """
    Added messages should show up in the request.session,
    fetched messages should be the same as the added ones,
    and fetching should clear the message list.
    """
    # Aquire a request object
    test_app.get('/')
    context = util.TEMPLATE_TEST_CONTEXT['mediagoblin/root.html']
    request = context['request']

    # The message queue should be empty
    #assert request.session.get('messages', []) == []
    assert request not in util.TEST_MESSAGES

    # Adding a message should modify the session accordingly
    add_message(request, 'herp_derp', 'First!')
    test_msg_queue = [{'text': 'First!', 'level': 'herp_derp'}]
    #assert request.session['messages'] == test_msg_queue
    assert util.TEST_MESSAGES[request] == test_msg_queue

    # fetch_messages should return and empty the queue
    assert fetch_messages(request) == test_msg_queue
    #assert request.session.get('messages') == []
    print request
    print util.TEST_MESSAGES
    assert request not in util.TEST_MESSAGES
