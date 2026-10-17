import re

from codeangel.io.errors import CodeangelError


class TemplateRenderer:
    _pattern = re.compile(r"\{\{([a-z_]+)\}\}")

    def render(self, text: str, variables: dict[str, str], where: str) -> str:
        return self._pattern.sub(lambda match: self._value(match, variables, where), text)

    def _value(self, match: re.Match[str], variables: dict[str, str], where: str) -> str:
        if match[1] not in variables:
            raise CodeangelError(f"{where}: no value for {{{{{match[1]}}}}}")
        return variables[match[1]]
