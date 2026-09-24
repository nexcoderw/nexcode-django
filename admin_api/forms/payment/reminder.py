from django import forms
from django.utils import timezone

from home.models import (
    PaymentReminderRule,
)


REMINDER_RULE_FIELDS = (
    "event",
    "timing",
    "days",
    "remind_on",
    "channel",
    "is_enabled",
)


class PaymentReminderRuleCreateForm(
    forms.Form
):
    event = forms.ChoiceField(
        choices=(
            PaymentReminderRule
            .Event.choices
        ),
    )

    timing = forms.ChoiceField(
        choices=(
            PaymentReminderRule
            .Timing.choices
        ),
    )

    days = forms.IntegerField(
        min_value=0,
        max_value=3650,
        required=False,
    )

    remind_on = forms.DateField(
        required=False,
    )

    channel = forms.ChoiceField(
        choices=(
            PaymentReminderRule
            .Channel.choices
        ),
        required=False,
    )

    is_enabled = (
        forms.BooleanField(
            required=False,
        )
    )

    def clean(self):
        data = super().clean()

        if (
            "days"
            not in self.data
        ):
            data["days"] = 0

        if (
            "channel"
            not in self.data
        ):
            data["channel"] = (
                PaymentReminderRule
                .Channel.IN_APP
            )

        if (
            "is_enabled"
            not in self.data
        ):
            data["is_enabled"] = True

        _validate_timing(
            self,
            data,
        )

        return data


class PaymentReminderRuleUpdateForm(
    forms.Form
):
    event = forms.ChoiceField(
        choices=(
            PaymentReminderRule
            .Event.choices
        ),
        required=False,
    )

    timing = forms.ChoiceField(
        choices=(
            PaymentReminderRule
            .Timing.choices
        ),
        required=False,
    )

    days = forms.IntegerField(
        min_value=0,
        max_value=3650,
        required=False,
    )

    remind_on = forms.DateField(
        required=False,
    )

    channel = forms.ChoiceField(
        choices=(
            PaymentReminderRule
            .Channel.choices
        ),
        required=False,
    )

    is_enabled = (
        forms.BooleanField(
            required=False,
        )
    )

    def __init__(
        self,
        *args,
        rule=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.rule = rule

    def clean(self):
        data = super().clean()

        supplied = (
            set(self.data.keys())
            & set(
                REMINDER_RULE_FIELDS
            )
        )

        if not supplied:
            raise forms.ValidationError(
                "No reminder rule "
                "changes were provided."
            )

        if not self.rule:
            return data

        merged = {}

        for field in (
            REMINDER_RULE_FIELDS
        ):
            if field in self.data:
                merged[field] = (
                    data.get(field)
                )
            else:
                merged[field] = (
                    getattr(
                        self.rule,
                        field,
                    )
                )

        _validate_timing(
            self,
            merged,
        )

        return data


def _validate_timing(
    form,
    data,
):
    timing = data.get(
        "timing"
    )

    days = (
        data.get(
            "days"
        )
        or 0
    )

    if (
        timing
        == (
            PaymentReminderRule
            .Timing.DATE
        )
    ):
        _validate_remind_on(
            form,
            data.get(
                "remind_on"
            ),
        )

        # A set date replaces the offset.
        return

    if (
        timing
        == (
            PaymentReminderRule
            .Timing.ON
        )
        and days != 0
    ):
        form.add_error(
            "days",
            (
                "On-date reminders "
                "must use zero days."
            ),
        )

    if (
        timing
        in (
            PaymentReminderRule
            .Timing.BEFORE,
            PaymentReminderRule
            .Timing.AFTER,
        )
        and days < 1
    ):
        form.add_error(
            "days",
            (
                "Before and after "
                "reminders require "
                "at least one day."
            ),
        )


def _validate_remind_on(
    form,
    remind_on,
):
    if not remind_on:
        form.add_error(
            "remind_on",
            (
                "Choose the date to "
                "send this reminder."
            ),
        )
        return

    # Only a newly chosen date must lie ahead; an unchanged date on
    # an existing rule may already have passed.
    if (
        "remind_on" in form.data
        and remind_on
        < timezone.localdate()
    ):
        form.add_error(
            "remind_on",
            (
                "Choose today or a "
                "later date."
            ),
        )
