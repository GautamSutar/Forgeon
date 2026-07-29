from __future__ import annotations

from app.parsers.html_form_parser import parse_html_form

SAMPLE_HTML = """
<form>
  <label for="fname">Full Name</label>
  <input type="text" id="fname" name="full_name" required />

  <label for="email">Email Address</label>
  <input type="email" id="email" name="email" required />

  <input type="hidden" name="csrf" value="abc" />

  <label>Resume</label>
  <input type="file" name="resume" />

  <select name="experience">
    <option value="0-1">0-1 years</option>
    <option value="2-4">2-4 years</option>
  </select>

  <textarea name="cover_letter" placeholder="Why do you want this role?"></textarea>

  <input type="radio" name="visa" value="yes" /> Yes
  <input type="radio" name="visa" value="no" /> No

  <button type="submit">Submit</button>
</form>
"""


def test_parse_html_form_extracts_visible_fields() -> None:
    fields = parse_html_form(SAMPLE_HTML)
    names = {f.name for f in fields}

    assert "csrf" not in names  # hidden fields excluded
    assert "full_name" in names
    assert "email" in names
    assert "resume" in names
    assert "experience" in names
    assert "cover_letter" in names
    assert "visa" in names


def test_parse_html_form_labels_and_required() -> None:
    fields = {f.name: f for f in parse_html_form(SAMPLE_HTML)}
    assert fields["full_name"].label == "Full Name"
    assert fields["full_name"].required is True
    assert fields["email"].type == "email"


def test_parse_html_form_select_options() -> None:
    fields = {f.name: f for f in parse_html_form(SAMPLE_HTML)}
    assert fields["experience"].options == ["0-1 years", "2-4 years"]


def test_parse_html_form_radio_group_deduped() -> None:
    fields = [f for f in parse_html_form(SAMPLE_HTML) if f.name == "visa"]
    assert len(fields) == 1
    assert set(fields[0].options) == {"Yes", "No"}


def test_parse_html_form_placeholder_used_as_label() -> None:
    fields = {f.name: f for f in parse_html_form(SAMPLE_HTML)}
    assert fields["cover_letter"].label == "Why do you want this role?"
