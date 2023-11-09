import reflex as rx

from . import routes
from .models import Field, FieldType, Option
from .state import State
from .form_editor import FormEditorState


class FieldEditorState(State):
    field: Field = Field()

    def handle_submit(self, form_data: dict[str, str]):
        self.field.name = form_data["name"]
        self.field.type_ = FieldType(form_data["type_"])
        self.field.required = bool(form_data.get("required"))
        return [
            FormEditorState.update_field(self.field),
            rx.redirect(routes.edit_form(self.form_id)),
        ]

    def handle_required_change(self, is_checked: bool):
        self.field.required = is_checked

    def load_field(self):
        if self.field_id == "new":
            self.field = Field(form_id=self.form_id)
        else:
            with rx.session() as session:
                self.field = session.get(Field, self.field_id)

    def set_type(self, type_: str):
        self.field.type_ = FieldType(type_)

    def set_field(self, key: str, value: str):
        setattr(self.field, key, value)

    def set_option(self, index: int, key: str, value: str):
        with rx.session() as session:
            session.add(self.field)
            if self.field.id is None:
                session.commit()
                session.refresh(self.field)
            option = self.field.options[index]
            option.field_id = self.field.id
            setattr(option, key, value)
            session.add(option)
            session.commit()
            session.refresh(self.field)

    def add_option(self):
        with rx.session() as session:
            session.add(self.field)
            if not self.field.id:
                session.commit()
                session.refresh(self.field)
            option = Option(field_id=self.field.id)
            self.field.options.append(option)

    def delete_option(self, index: int):
        with rx.session() as session:
            session.add(self.field)
            option_to_delete = session.get(Option, self.field.options[index].id)
            del self.field.options[index]
            session.delete(option_to_delete)
            session.commit()
            session.refresh(self.field)


def option_editor(option: Option, index: int):
    return rx.hstack(
        rx.form_label(
            "Label",
            rx.input(
                placeholder="Label",
                value=option.label,
                on_change=lambda v: FieldEditorState.set_option(index, "label", v),
            ),
        ),
        rx.form_label(
            "Value",
            rx.input(
                placeholder=rx.cond(option.label != "", option.label, "Value"),
                value=option.value,
                on_change=lambda v: FieldEditorState.set_option(index, "value", v),
            ),
        ),
        rx.button("X", on_click=FieldEditorState.delete_option(index)),
    )


def options_editor():
    return rx.fragment(
        rx.foreach(FieldEditorState.field.options, option_editor),
        rx.button("Add Option", on_click=FieldEditorState.add_option()),
    )


def field_editor_input(key: str):
    return rx.form_label(
        key.capitalize(),
        rx.input(
            placeholder=key.capitalize(),
            name=key,
            value=getattr(FieldEditorState.field, key),
            on_change=lambda v: FieldEditorState.set_field(key, v),
        ),
    )


def field_editor():
    return rx.form(
        field_editor_input("name"),
        field_editor_input("prompt"),
        rx.form_label(
            "Type",
            rx.select(
                *[rx.option(t.value, value=t.value) for t in FieldType],
                name="type_",
                value=FieldEditorState.field.type_.to(str),
                on_change=FieldEditorState.set_type,
            ),
        ),
        rx.form_label(
            "Required",
            rx.checkbox(
                name="required",
                is_checked=FieldEditorState.field.required,
                on_change=FieldEditorState.handle_required_change,
            ),
        ),
        rx.cond(
            rx.Var.create(
                [
                    FieldType.select.value,
                    FieldType.radio.value,
                    FieldType.checkbox.value,
                ]
            ).contains(FieldEditorState.field.type_),
            options_editor(),
        ),
        rx.button("Save", type_="submit"),
        on_submit=FieldEditorState.handle_submit,
    )


def field_editor_modal():
    return rx.modal(
        header="Edit Field",
        body=field_editor(),
        is_open=State.field_id != "",
        on_close=rx.redirect(routes.edit_form(State.form_id)),
    )