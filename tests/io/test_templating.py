from __future__ import annotations

import pytest

from codeangel.io.errors import CodeangelError
from codeangel.io.templating import TemplateRenderer


class TestTemplateRenderer:
    def test_substitutes_known_variables(self):
        assert TemplateRenderer().render("{{a}}", {"a": "b"}, "here") == "b"

    def test_unknown_variable_raises_codeangel_error(self):
        with pytest.raises(CodeangelError) as caught:
            TemplateRenderer().render("{{missing}}", {}, "here")
        message = str(caught.value)
        assert "missing" in message
        assert "here" in message
