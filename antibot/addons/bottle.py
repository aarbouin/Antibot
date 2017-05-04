import bottle

TEMPLATE_UTILS = """
    <link rel="stylesheet" href="//aui-cdn.atlassian.com/aui-hipchat/0.1.2/css/aui-hipchat.min.css"/>
    <script type="text/javascript" src="//code.jquery.com/jquery-2.2.2.min.js"></script>
    <script type="text/javascript" src="//aui-cdn.atlassian.com/aui-hipchat/0.1.2/js/aui-hipchat.min.js"></script>
    <script src="//www.hipchat.com/atlassian-connect/all.js"></script>
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
