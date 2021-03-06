import re


def _compile(path):
    return re.compile(re.sub('<([^\/]*)>', '(?P<\\1>[^\/]*)', path))


class Router(object):
    '''
    A simple, asynchronous event router.
    '''

    def __init__(self, methods=[ 'get', 'head', 'post', 'put', 'delete', 'connect', 'options', 'trace', 'patch' ]):
        self.__routes__ = { }
        self.__methods__ = methods

    def __getattribute__(self, name):
        if name in super(Router, self).__getattribute__('__methods__'):
            return lambda path: self.route(name, path)
        else:
            return super(Router, self).__getattribute__(name)

    def _check_method(self, method):
        if not method in self.__methods__:
            raise Exception(f'Method error: {method} not in {self.__methods__}')

    def _get_paths(self, method):
        self._check_method(method)
        if not self.__routes__.get(method):
            self.__routes__[method] = { }
        return self.__routes__[method]

    def _match(self, method, path):
        self._check_method(method)
        paths = self.__routes__.get(method)
        if not paths:
            return None
        for (regex, handler) in paths.items():
            match = regex.fullmatch(path)
            if match:
                return (handler, match.groupdict())
        return None

    def route(self, method, path):
        '''
        Add `method` to `path`. Should be used as a decorator.

        :param method: The `method` of the route.
        :param path: The `path` of the route.
        '''
        def wrapper(handler):
            paths = self._get_paths(method)
            paths[_compile(path)] = handler
        return wrapper

    async def emit(self, method, path, *args, **kargs):
        '''
        Trigger a `method` event for `path`.

        :param method: The `method` to emit.
        :param path: The `path` to emit to.
        :param \*args: The arguments to provide to handlers.
        :param \*\*kargs: The keyword arguments to provide to handlers.
        '''
        handler, groupdict = self._match(method, path)
        kargs.update(groupdict)
        if not handler:
            return None
        return await handler(*args, **kargs)
