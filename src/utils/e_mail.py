"""
e_mail.py
---------
Version 1.0, updated on 2025-05-01

"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from logger import Logger
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.data_utils import is_none_or_empty


class EMail(LoggingMixin):
    """
    EMail class.

    This class is for sending emails using SMTP. It allows for configuration
    through environment variables.

    Attributes
    ----------
    out_server_name : str
        Outgoing server name used for sending emails.

    port : int
        Port used for the outgoing mail server.

    user_name : str
        Username for logging into the outgoing mail server.

    password : str
        Password for logging into the outgoing mail server.

    mail_from : str
        The sender's email address.

    mail_to : str
        The recipient's email address.

    Methods
    -------
    send(subject: str, body: str) -> None
       Sends an e-mail to the user of this program.

    Notes
    -----
    Ensure the following environment variables are set:

        - OUTGOING_MAIL_SERVER: The SMTP server address.
        - OUTGOING_MAIL_PORT: The SMTP server port.
        - OUTGOING_SERVER_USER: The username for the SMTP server.
        - OUTGOING_SERVER_PW: The password for the SMTP server.
        - OUTGOING_MAIL_SENDER: The email address from which the email will be
          sent.
        - OUTGOING_MAIL_RECIPIENT: The recipient's email address.

    """

    def __init__(self):
        """
        Constructor.

        Initializes the EMail class

        """

        self._mail_to = None
        self._mail_from = None
        self._password = None
        self._user_name = None
        self._port = None
        self._out_server_name = None

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

    # region --- Properties

    @property
    def out_server_name(self) \
            -> str:
        """
        Returns the outgoing server name used for sending emails.

        If the property is not set yet, the _set_out_server_name method is
        called to set it automatically.

        """

        if is_none_or_empty(self._out_server_name):
            self._set_out_server_name()
        return self._out_server_name

    @out_server_name.setter
    def out_server_name(self, server_name: str) \
            -> None:
        """
        Sets the outgoing server name used for sending emails.
        """

        self._out_server_name = server_name

    @property
    def port(self) \
            -> int:
        """
        Returns the port used for the outgoing mail server.

        If the port is not set yet, the _set_port method is called to set
        the port automatically.

        """
        if is_none_or_empty(self._port):
            self._set_port()

        return self._port

    @port.setter
    def port(self, server: int) \
            -> None:
        """
        Sets the port used for the outgoing mail server.
        """

        self._port = server

    @property
    def user_name(self) \
            -> str:
        """
        Returns the username for logging into the outgoing mail server.

        If the username is not set yet, the _set_user_name method is called
        to set the username automatically.

        """

        if is_none_or_empty(self._user_name):
            self._set_user_name()
        return self._user_name

    @user_name.setter
    def user_name(self, server: str) \
            -> None:
        """
        Sets the username for logging into the outgoing mail server.
        """

        self._user_name = server

    @property
    def password(self) \
            -> str:
        """
        Returns the password for logging into the outgoing mail server.

        If the password is not set yet, the _set_password method is called
        to set the password automatically.

        """

        if is_none_or_empty(self._password):
            self._set_password()
        return self._password

    @password.setter
    def password(self, server: str) \
            -> None:
        """
        Sets the password for logging into the outgoing mail server.
        """

        self._password = server

    @property
    def mail_from(self) \
            -> str:
        """
        Returns the sender's email address.

        If the address is not set yet, the _set_mail_from method is called
        to set the address automatically.

        """

        if is_none_or_empty(self._mail_from):
            self._set_mail_from()
        return self._mail_from

    @mail_from.setter
    def mail_from(self, server: str) \
            -> None:
        """
        Sets the sender's email address.
        """

        self._mail_from = server

    @property
    def mail_to(self) \
            -> str:
        """
        Returns the recipient's email address.

        If the address is not set yet, the _set_mail_to method is called
        to set the address automatically.

        """
        if is_none_or_empty(self._mail_to):
            self._set_mail_to()
        return self._mail_to

    @mail_to.setter
    def mail_to(self, server: str) \
            -> None:
        """
        Sets the recipient's email address.
        """

        self._mail_to = server

    # endregion --- Properties

    # region --- Public Methods
    def send(self, subject: str, body: str) \
            -> None:
        """
        Sends an e-mail to the user of this program.

        Parameters
        ----------
        subject: str
            The subject of the e-mail to send.

        body: str
            The body of the e-mail to send.

        Notes
        -----
        This method gets the credentials needed for sending an e-mail from the
        following environment variables:

        - OUTGOING_MAIL_SERVER
        - OUTGOING_MAIL_PORT
        - OUTGOING_SERVER_USER
        - OUTGOING_SERVER_PW
        - OUTGOING_MAIL_SENDER
        - OUTGOING_MAIL_RECIPIENT

        Make sure you have set these environment variables if you want to use
        this method.

        """

        try:
            server = self._get_outgoing_server()

            # Login to the email account
            server.login(self.user_name, self.password)

            # Create the email
            msg = MIMEMultipart()
            msg['From'] = self.mail_from
            msg['To'] = self.mail_to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            server.send_message(msg)

            # Disconnect from the server
            server.quit()

            msg = "E-mail sent successfully!"
            self._log(msg, 'info')

        except Exception as err:
            msg = f"Failed to send e-mail. Error: {err}"
            self._log(msg, 'error')
            raise

    # endregion --- Public Methods

    # region --- Protected Methods

    def _get_outgoing_server(self) \
            -> smtplib.SMTP_SSL | smtplib.SMTP:
        """
        Sets up the outgoing mail server and returns it.

        Returns
        -------
        SMTP_SSL | SMTP
            The outgoing mail server object.

        """
        if self.port == 465:
            return smtplib.SMTP_SSL(self.out_server_name, self.port)

        server = smtplib.SMTP(self.out_server_name, self.port)
        server.starttls()
        return server

    def _set_out_server_name(self) \
            -> None:
        """
        Sets the outgoing server name from the environment variables.

        Sets the outgoing server name from the environment variable
        'OUTGOING_MAIL_SERVER'.

        Raises
        ------
        CriticalException
            If the corresponding environment variable does not exist or
            returns an empty string.

        """

        self._out_server_name = os.getenv('OUTGOING_MAIL_SERVER')
        if not self._out_server_name:
            raise CriticalException(
                self.logger,
                "OUTGOING_MAIL_SERVER environment variable is not set."
            )

    def _set_port(self) \
            -> None:
        """
        Sets the outgoing mail server port from the environment variables.

        Sets the outgoing mail server port from the environment variable
        'OUTGOING_MAIL_PORT`.

        Raises
        ------
        CriticalException
            If the corresponding environment variable does not exist or
            returns an empty string.

        """

        self._port = int(os.getenv('OUTGOING_MAIL_PORT'))
        if not self._port:
            raise CriticalException(
                self.logger,
                "OUTGOING_MAIL_PORT environment variable is not set."
            )

    def _set_user_name(self) \
            -> None:
        """
        Sets the username from the environment variables.

        Sets the username from the environment variable 'OUTGOING_SERVER_USER'.

        Raises
        ------
        CriticalException
            If the corresponding environment variable does not exist or
            returns an empty string.

        """
        self._user_name = os.getenv('OUTGOING_SERVER_USER')
        if not self._user_name:
            raise CriticalException(
                self.logger,
                "OUTGOING_SERVER_USER environment variable is not set."
            )

    def _set_password(self) \
            -> None:
        """
        Sets the password from the environment variables.

        Sets the password from the environment variable 'OUTGOING_SERVER_PW'.

        Raises
        ------
        CriticalException
            If the corresponding environment variable does not exist or
            returns an empty string.

        """
        self._password = os.getenv('OUTGOING_SERVER_PW')
        if not self._password:
            raise CriticalException(
                self.logger,
                "OUTGOING_SERVER_PW environment variable is not set."
            )

    def _set_mail_from(self) \
            -> None:
        """
        Sets the sender's email address from the environment variables.

        Sets the sender's email address from the environment variable
        'OUTGOING_MAIL_SENDER`.

        Raises
        ------
        CriticalException
            If the corresponding environment variable does not exist or
            returns an empty string.

        """

        self._mail_from = os.getenv('OUTGOING_MAIL_SENDER')
        if not self._mail_from:
            raise CriticalException(
                self.logger,
                "OUTGOING_MAIL_SENDER environment variable is not set."
            )

    def _set_mail_to(self) \
            -> None:
        """
        Sets the recipient's email address from the environment variable.

        Sets the recipient's email address from the environment variable
        'OUTGOING_MAIL_RECIPIENT'.

        Raises
        ------
        CriticalException
            If the corresponding environment variable does not exist or
            returns an empty string.

        """

        self._mail_to = os.getenv('OUTGOING_MAIL_RECIPIENT')
        if not self._mail_to:
            raise CriticalException(
                self.logger,
                "OUTGOING_MAIL_RECIPIENT environment variable is not set."
            )

    # endregion --- Protected Methods
