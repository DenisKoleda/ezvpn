# Manual Testing Plan for Refactored VPN Bot

This plan outlines the key functionalities to test manually to ensure the refactored bot is working as expected.

**Prerequisites:**
*   Set up the `.env` file with valid credentials (Bot Token, YooKassa Token, DB connection, VPN API details).
*   Ensure MongoDB is running and accessible.
*   Ensure the VPN server API is accessible.
*   Install dependencies from `req.txt`.
*   Run the bot using `python src/bot/app.py`.

**I. User Registration and Initial Interaction**
1.  **New User**:
    *   Send `/start` to the bot as a completely new Telegram user.
    *   **Expected**: Welcome message is displayed with the main menu keyboard. User is added to the database (`users` collection) with correct initial details (telegram_id, name, registration_date, tarif=None, test_active=True).
2.  **Existing User**:
    *   Send `/start` as a user already in the database.
    *   **Expected**: Welcome message and main menu. No new user entry created; existing entry is not erroneously modified.

**II. Main Menu Navigation**
Test each main menu button:
1.  **КУПИТЬ VPN**:
    *   **User without active tariff**: Click button.
        *   **Expected**: Message "Доступные тарифы:" and inline keyboard `sub_inline_markup` (with "Уверенная соточка") are shown.
    *   **User with active tariff**: Click button.
        *   **Expected**: Warning message about existing subscription, then "Доступные тарифы:" and `sub_inline_markup`.
2.  **МОЙ ТАРИФ**:
    *   **User without active tariff**: Click button.
        *   **Expected**: Message "У вас нет подписки :(".
    *   **User with active tariff**: Click button.
        *   **Expected**: Message displaying current tariff name and expiry date, with `bnt_usr_main` inline keyboard (Продлить, Скачать, Удалить). Verify date format is DD/MM/YYYY.
3.  **УПРАВЛЕНИЕ ТАРИФОМ**:
    *   **User without active tariff**: Click button.
        *   **Expected**: Message "У вас нет подписки :(".
    *   **User with active tariff**: Click button.
        *   **Expected**: Message about server selection and `srv1_kb` inline keyboard.
4.  **ТЕХ.ПОДДЕРЖКА**:
    *   Click button.
        *   **Expected**: Message "Чат тех.поддержки: vk.com".
5.  **ИНСТРУКЦИЯ**:
    *   Click button.
        *   **Expected**: Message "Инструкции по настройке VPN..." and `bnt_intsr_Menu` keyboard.
6.  **ГЛАВНОЕ МЕНЮ** (if navigating from a sub-menu keyboard that has this option):
    *   Click button.
        *   **Expected**: Message "Панель управления VPN аккаунтом" and `mainMenu` keyboard.

**III. Payment Flows**
1.  **New Subscription ('Уверенная соточка' - tarif1)**:
    *   From `sub_inline_markup`, click "Уверенная соточка".
    *   **Expected**: Invoice is sent via YooKassa.
    *   Complete payment (using test payment details if possible).
    *   **Expected**: Successful payment message. User's record in DB (`users` collection) updated with `tarif="Уверенная соточка"` and `tarif_exp` set to 30 days from now.
2.  **Renew Subscription ('resume_tarif')**:
    *   From "МОЙ ТАРИФ" (for a user with an existing, possibly expiring tariff), click "Продлить тариф" (`resume_tarif` callback from `bnt_usr_main`).
    *   **Expected**: Invoice for renewal is sent.
    *   Complete payment.
    *   **Expected**: Successful payment message. User's `tarif_exp` in DB is extended by 30 days from the *previous* expiry date.

**IV. Server Management (VPN Configuration)**
(Requires user to have an active tariff)
1.  **Navigate to Server Management**:
    *   Click "УПРАВЛЕНИЕ ТАРИФОМ" -> Select "Россия #1" (`srv1_rus_1` from `srv1_kb`).
    *   **Expected**: Message about "Сервер Россия #1" and `srv1_rus_1_kb` (Создать аккаунт, Назад).
2.  **Create VPN Account (`add_srv1_rus_1`)**:
    *   Click "Создать аккаунт".
    *   **Expected**:
        *   If user previously had a config on this server, it's deleted from VPN provider and DB.
        *   A new VPN peer is created on the VPN server API.
        *   A new entry is added to `uslugi` collection in DB (with `telegram_id`, `preshared_key`, `tarif_ip`, `srv_id="srv1_rus_1"`).
        *   Success message "Аккаунт создан!..." sent to user.
        *   **Verify**: Check for IP/key conflict resolution if trying multiple times or with forced conflicts (harder to test manually without specific tools).
3.  **Download VPN Config (`download_config`)**:
    *   From "МОЙ ТАРИФ", click "Скачать конфиг" (`download_config` callback from `bnt_usr_main`). (User must have a config created from step IV.2).
    *   **Expected**:
        *   Bot sends a `.conf` file.
        *   Bot sends a `.png` QR code image.
        *   Message "Ваши данные для подключения!".
        *   **Verify**: Content of `.conf` file should be valid.
4.  **Delete VPN Config (`delete_config`)**:
    *   From "МОЙ ТАРИФ", click "Удалить конфиг" (`delete_config` callback from `bnt_usr_main`).
    *   **Expected**:
        *   VPN peer is deleted from the VPN server API.
        *   Entry is removed from `uslugi` collection in DB.
        *   Success message "Удалено конфигураций: 1" (or similar) sent to user.
        *   Trying to download again should fail or state no config found.

**V. Background Task (`vps_update`)**
This is harder to test directly without waiting or manipulating system time/DB entries.
1.  **Subscription Expiry**:
    *   Manually set a user's `tarif_exp` in the DB to a past date.
    *   Wait for the `vps_update_task` to run (default every 4 hours, can be shortened for testing in `scheduler.py`).
    *   **Expected**:
        *   User receives an expiry notification message.
        *   User's `tarif` and `tarif_exp` are set to `None` in DB.
        *   Associated VPN config is deleted from `uslugi` collection in DB.
        *   Associated VPN peer is deleted from the VPN server API.

**VI. Error Handling and Edge Cases**
*   Try invalid commands.
*   Interact with buttons in unexpected order (if possible).
*   Test what happens if VPN API or DB is temporarily unavailable (harder to simulate, but observe bot behavior if such issues occur).
*   Test with non-ASCII characters in names/messages if applicable.
```
