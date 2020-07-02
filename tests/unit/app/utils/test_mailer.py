import pytest


@pytest.mark.parametrize(
    "mail_type, token_type, mail_subject",
    [
        (
            "user_activation",
            "user_activation",
            "Test Master Organization: Activate my account.",
        ),
        (
            "reset_password",
            "reset_password",
            "Test Master Organization: Reset my password.",
        ),
    ],
)
def test_send_template_email(
    test_client,
    initialize_database,
    mock_mailing_client,
    create_master_organization,
    create_admin_user,
    mail_type,
    token_type,
    mail_subject,
):
    from app.server.utils.mailer import Mailer

    mailing_client = Mailer(organization=create_master_organization)
    token = create_admin_user.encode_single_use_jws(token_type=token_type)
    mailing_client.send_template_email(
        mail_type=mail_type,
        token=token,
        email=create_admin_user.email,
        given_names=create_admin_user.given_names,
    )

    mails = mock_mailing_client
    assert len(mails) == 1
    assert mails[0].get("subject") == mail_subject
