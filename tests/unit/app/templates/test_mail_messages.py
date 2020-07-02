from app.server.templates.mail_messages import MailMessage


def test_activate_user_mail_message(test_client, create_master_organization):
    mail_message_template = MailMessage(organization_name=create_master_organization.name)
    action_tag, mail_message = mail_message_template.activate_user_mail_message()
    assert f'{create_master_organization.name}: Activate my account.' in action_tag
    assert f'Thank you for registering an admin account with {create_master_organization.name}.' in mail_message


def test_reset_user_password_mail_message(test_client, create_master_organization):
    mail_message_template = MailMessage(organization_name=create_master_organization.name)
    action_tag, mail_message = mail_message_template.reset_user_password_mail_message()
    assert f'{create_master_organization.name}: Reset my password.' in action_tag
    assert f'You requested to reset the password for your {create_master_organization.name} account.' in mail_message
