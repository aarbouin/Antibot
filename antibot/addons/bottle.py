from json import dumps

import bottle

TEMPLATE_UTILS = """
    <!--  AUI Core -->
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
    <script src="//aui-cdn.atlassian.com/aui-adg/6.0.9/js/aui.js"></script>
    <link rel="stylesheet" href="//aui-cdn.atlassian.com/aui-adg/6.0.9/css/aui.min.css" media="all">
    
    <!--  AUI Hipchat -->
    <script src="//www.hipchat.com/atlassian-connect/all.js"></script>
    <link rel="stylesheet" href="//aui-cdn.atlassian.com/aui-hipchat/0.1.2/css/aui-hipchat.min.css"/>
    <!--<script type="text/javascript" src="//aui-cdn.atlassian.com/aui-hipchat/0.1.2/js/aui-hipchat.min.js"></script>-->
    
    <!-- AUI Experimental components -->
    <link rel="stylesheet" href="//aui-cdn.atlassian.com/aui-adg/6.0.9/css/aui-experimental.min.css" media="all">
    <script src="//aui-cdn.atlassian.com/aui-adg/6.0.9/js/aui-experimental.min.js"></script>
    
    <!-- AUI Datepicker and Soy templates -->
    <script src="//aui-cdn.atlassian.com/aui-adg/6.0.9/js/aui-datepicker.js"></script>
    <script src="//aui-cdn.atlassian.com/aui-adg/6.0.9/js/aui-soy.js"></script>
    <script>
        $(document).ready(function () {
            var theme = getQueryVariable('theme');

            if (theme === 'light' || theme === 'dark') {
                $('body').addClass(theme);
            }

            function getQueryVariable(variable) {
                var query = window.location.search.substring(1);
                var vars = query.split("&");
                for (var i = 0; i < vars.length; i++) {
                    var pair = vars[i].split("=");
                    if (pair[0] == variable) {
                        return pair[1];
                    }
                }
                return false;
            }
        });
    </script>
"""


def template(file, *args, **kwargs):
    kwargs['hipchatTools'] = TEMPLATE_UTILS
    return bottle.template(file, *args, **kwargs)


def jsify(object):
    return dumps(object).replace('\'', '\\\'')
