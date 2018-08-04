import click
import inspect as _inspect

from click import *
from click.formatting import join_options as _join_options
from click.utils import make_default_short_help as _make_default_short_help


CLI_HELP_STRING_MAX_LEN = 120
DEFAULT_CONTEXT_SETTINGS = dict(help_option_names=('-h', '--help'))


def _update_ctx_settings(context_settings):
    rv = DEFAULT_CONTEXT_SETTINGS.copy()
    if not context_settings:
        return rv
    rv.update(context_settings)
    return rv


class Command(click.Command):
    """
    Commands are the basic building block of command line interfaces in
    Click.  A basic command handles command line parsing and might dispatch
    more parsing to commands nested below it.

    :param name: the name of the command to use unless a group overrides it.
    :param context_settings: an optional dictionary with defaults that are
                             passed to the context object.
    :param params: the parameters to register with this command.  This can
                   be either :class:`Option` or :class:`Argument` objects.
    :param help: the help string to use for this command.
    :param epilog: like the help string but it's printed at the end of the
                   help page after everything else.
    :param short_help: the short help to use for this command.  This is
                       shown on the command listing of the parent command.
    :param add_help_option: by default each command registers a ``--help``
                            option.  This can be disabled by this parameter.
    :param options_metavar: The options metavar to display in the usage.
                            Defaults to ``[OPTIONS]``.
    """
    def __init__(self, name, context_settings=None, callback=None, params=None,
                 help=None, epilog=None, short_help=None, add_help_option=True,
                 options_metavar='[OPTIONS]'):
        super().__init__(
            name, callback=callback, params=params, help=help, epilog=epilog,
            short_help=short_help, add_help_option=add_help_option,
            context_settings=_update_ctx_settings(context_settings),
            options_metavar=options_metavar)

        # FIXME: these two lines are for backwards compatibility with click 6.7,
        # FIXME: and should be removed once on 7+
        self.short_help = short_help
        self.short_help = self.get_short_help_str()

    # overridden to support displaying args before the options metavar
    def collect_usage_pieces(self, ctx):
        rv = []
        for param in self.get_params(ctx):
            rv.extend(param.get_usage_pieces(ctx))
        rv.append(self.options_metavar)
        return rv

    # overridden to print arguments first, separately from options
    def format_options(self, ctx, formatter):
        args = []
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                if isinstance(param, click.Argument):
                    args.append(rv)
                else:
                    opts.append(rv)
        if args:
            with formatter.section('Arguments'):
                formatter.write_dl(args)
        if opts:
            with formatter.section(self.options_metavar):
                formatter.write_dl(opts)

    # overridden to set the limit parameter to always be CLI_HELP_STRING_MAX_LEN
    def get_short_help_str(self, limit=0):
        if self.short_help:
            return self.short_help
        elif not self.help:
            return ''
        rv = _make_default_short_help(self.help, CLI_HELP_STRING_MAX_LEN)
        return rv


class GroupOverrideMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, context_settings=_update_ctx_settings(
            kwargs.pop('context_settings', None)), **kwargs)
        self.subcommand_metavar = 'COMMAND [<args>...]'
        self.subcommands_metavar = 'COMMAND1 [<args>...] [COMMAND2 [<args>...]]'

        # FIXME: these two lines are for backwards compatibility with click 6.7,
        # FIXME: and should be removed once on 7+
        self.short_help = kwargs.get('short_help')
        self.short_help = self.get_short_help_str()

    def command(self, *args, **kwargs):
        """
        Commands are the basic building block of command line interfaces in
        Click.  A basic command handles command line parsing and might dispatch
        more parsing to commands nested below it.

        :param name: the name of the command to use unless a group overrides it.
        :param context_settings: an optional dictionary with defaults that are
                                 passed to the context object.
        :param params: the parameters to register with this command.  This can
                       be either :class:`Option` or :class:`Argument` objects.
        :param help: the help string to use for this command.
        :param epilog: like the help string but it's printed at the end of the
                       help page after everything else.
        :param short_help: the short help to use for this command.  This is
                           shown on the command listing of the parent command.
        :param add_help_option: by default each command registers a ``--help``
                                option.  This can be disabled by this parameter.
        :param options_metavar: The options metavar to display in the usage.
                                Defaults to ``[OPTIONS]``.
        :param args_before_options: Whether or not to display the options
                                            metavar before the arguments.
                                            Defaults to False.
        """
        return super().command(
            *args, cls=kwargs.pop('cls', Command) or click.Command, **kwargs)

    def collect_usage_pieces(self, ctx):
        if self.chain:
            rv = [self.subcommands_metavar]
        else:
            rv = [self.subcommand_metavar]
        rv.extend(click.Command.collect_usage_pieces(self, ctx))
        return rv

    # overridden to set the limit parameter to always be CLI_HELP_STRING_MAX_LEN
    def get_short_help_str(self, limit=0):
        if self.short_help:
            return self.short_help
        elif not self.help:
            return ''
        return _make_default_short_help(self.help, CLI_HELP_STRING_MAX_LEN)


class Group(GroupOverrideMixin, click.Group):
    """
    A group allows a command to have subcommands attached.  This is the
    most common way to implement nesting in Click.

    :param name: the name of the group (optional)
    :param commands: a dictionary of commands.
    """

    def group(self, *args, **kwargs):
        """
        A group allows a command to have subcommands attached.  This is the
        most common way to implement nesting in Click.

        :param name: the name of the group (optional)
        :param commands: a dictionary of commands.
        """
        return super().group(
            *args, cls=kwargs.pop('cls', Group) or Group, **kwargs)


class Argument(click.Argument):
    """
    Arguments are positional parameters to a command.  They generally
    provide fewer features than options but can have infinite ``nargs``
    and are required by default.

    :param param_decls: the parameter declarations for this option or
                        argument.  This is a list of flags or argument
                        names.
    :param type: the type that should be used.  Either a :class:`ParamType`
                 or a Python type.  The later is converted into the former
                 automatically if supported.
    :param required: controls if this is optional or not.
    :param default: the default value if omitted.  This can also be a callable,
                    in which case it's invoked when the default is needed
                    without any arguments.
    :param callback: a callback that should be executed after the parameter
                     was matched.  This is called as ``fn(ctx, param,
                     value)`` and needs to return the value.  Before Click
                     2.0, the signature was ``(ctx, value)``.
    :param nargs: the number of arguments to match.  If not ``1`` the return
                  value is a tuple instead of single value.  The default for
                  nargs is ``1`` (except if the type is a tuple, then it's
                  the arity of the tuple).
    :param metavar: how the value is represented in the help page.
    :param expose_value: if this is `True` then the value is passed onwards
                         to the command callback and stored on the context,
                         otherwise it's skipped.
    :param is_eager: eager values are processed before non eager ones.  This
                     should not be set for arguments or it will inverse the
                     order of processing.
    :param envvar: a string or list of strings that are environment variables
                   that should be checked.
    :param help: the help string.
    :param hidden: hide this option from help outputs.
                   Default is True, unless :param:`help` is given.
    """
    def __init__(self, param_decls, required=None, help=None, hidden=None, **attrs):
        super().__init__(param_decls, required=required, **attrs)
        self.help = help
        self.hidden = hidden if hidden is not None else not help

    # overridden to customize the automatic formatting of metavars
    # for example, given self.name = 'query':
    # upstream | (optional) | this-method | (optional)
    # default behavior:
    # QUERY    | [QUERY]    | <query>     | [<query>]
    # when nargs > 1:
    # QUERY... | [QUERY...] | <query>, ... | [<query>, ...]
    def make_metavar(self):
        if self.metavar is not None:
            return self.metavar
        var = '' if self.required else '['
        var += '<' + self.name + '>'
        if self.nargs != 1:
            var += ', ...'
        if not self.required:
            var += ']'
        return var

    # this code is 90% copied from click.Option.get_help_record
    def get_help_record(self, ctx):
        if self.hidden:
            return

        any_prefix_is_slash = []

        def _write_opts(opts):
            rv, any_slashes = _join_options(opts)
            if any_slashes:
                any_prefix_is_slash[:] = [True]
            rv += ': ' + self.make_metavar()
            return rv

        rv = [_write_opts(self.opts)]
        if self.secondary_opts:
            rv.append(_write_opts(self.secondary_opts))

        help = self.help or ''
        extra = []

        if self.default is not None:
            if isinstance(self.default, (list, tuple)):
                default_string = ', '.join('%s' % d for d in self.default)
            elif _inspect.isfunction(self.default):
                default_string = "(dynamic)"
            else:
                default_string = self.default
            extra.append('default: {}'.format(default_string))

        if self.required:
            extra.append('required')
        if extra:
            help = '%s[%s]' % (help and help + '  ' or '', '; '.join(extra))

        return ((any_prefix_is_slash and '; ' or ' / ').join(rv), help)


def command(name=None, cls=None, **attrs):
    """
    Commands are the basic building block of command line interfaces in
    Click.  A basic command handles command line parsing and might dispatch
    more parsing to commands nested below it.

    :param name: the name of the command to use unless a group overrides it.
    :param context_settings: an optional dictionary with defaults that are
                             passed to the context object.
    :param params: the parameters to register with this command.  This can
                   be either :class:`Option` or :class:`Argument` objects.
    :param help: the help string to use for this command.
    :param epilog: like the help string but it's printed at the end of the
                   help page after everything else.
    :param short_help: the short help to use for this command.  This is
                       shown on the command listing of the parent command.
    :param add_help_option: by default each command registers a ``--help``
                            option.  This can be disabled by this parameter.
    :param options_metavar: The options metavar to display in the usage.
                            Defaults to ``[OPTIONS]``.
    :param args_before_options: Whether or not to display the options
                                        metavar before the arguments.
                                        Defaults to False.
    """
    return click.command(name=name, cls=cls or Command, **attrs)


def group(name=None, cls=None, **attrs):
    """
    A group allows a command to have subcommands attached.  This is the
    most common way to implement nesting in Click.

    :param name: the name of the group (optional)
    :param commands: a dictionary of commands.
    :param name: the name of the command to use unless a group overrides it.
    :param context_settings: an optional dictionary with defaults that are
                             passed to the context object.
    :param help: the help string to use for this command.
    :param epilog: like the help string but it's printed at the end of the
                   help page after everything else.
    :param short_help: the short help to use for this command.  This is
                       shown on the command listing of the parent command.
    """
    return click.group(name=name, cls=cls or Group, **attrs)


def argument(*param_decls, cls=None, **attrs):
    """
    Arguments are positional parameters to a command.  They generally
    provide fewer features than options but can have infinite ``nargs``
    and are required by default.

    :param param_decls: the parameter declarations for this option or
                        argument.  This is a list of flags or argument
                        names.
    :param type: the type that should be used.  Either a :class:`ParamType`
                 or a Python type.  The later is converted into the former
                 automatically if supported.
    :param required: controls if this is optional or not.
    :param default: the default value if omitted.  This can also be a callable,
                    in which case it's invoked when the default is needed
                    without any arguments.
    :param callback: a callback that should be executed after the parameter
                     was matched.  This is called as ``fn(ctx, param,
                     value)`` and needs to return the value.  Before Click
                     2.0, the signature was ``(ctx, value)``.
    :param nargs: the number of arguments to match.  If not ``1`` the return
                  value is a tuple instead of single value.  The default for
                  nargs is ``1`` (except if the type is a tuple, then it's
                  the arity of the tuple).
    :param metavar: how the value is represented in the help page.
    :param expose_value: if this is `True` then the value is passed onwards
                         to the command callback and stored on the context,
                         otherwise it's skipped.
    :param is_eager: eager values are processed before non eager ones.  This
                     should not be set for arguments or it will inverse the
                     order of processing.
    :param envvar: a string or list of strings that are environment variables
                   that should be checked.
    :param help: the help string.
    :param hidden: hide this option from help outputs.
                   Default is True, unless help is given.
    """
    return click.argument(*param_decls, cls=cls or Argument, **attrs)


def option(*param_decls, **attrs):
    """
    Options are usually optional values on the command line and
    have some extra features that arguments don't have.

    :param param_decls: the parameter declarations for this option or
                        argument.  This is a list of flags or argument
                        names.
    :param show_default: controls if the default value should be shown on the
                         help page.  Normally, defaults are not shown.
    :param prompt: if set to `True` or a non empty string then the user will
                   be prompted for input if not set.  If set to `True` the
                   prompt will be the option name capitalized.
    :param confirmation_prompt: if set then the value will need to be confirmed
                                if it was prompted for.
    :param hide_input: if this is `True` then the input on the prompt will be
                       hidden from the user.  This is useful for password
                       input.
    :param is_flag: forces this option to act as a flag.  The default is
                    auto detection.
    :param flag_value: which value should be used for this flag if it's
                       enabled.  This is set to a boolean automatically if
                       the option string contains a slash to mark two options.
    :param multiple: if this is set to `True` then the argument is accepted
                     multiple times and recorded.  This is similar to ``nargs``
                     in how it works but supports arbitrary number of
                     arguments.
    :param count: this flag makes an option increment an integer.
    :param allow_from_autoenv: if this is enabled then the value of this
                               parameter will be pulled from an environment
                               variable in case a prefix is defined on the
                               context.
    :param help: the help string.
    """
    return click.option(*param_decls, **attrs)
