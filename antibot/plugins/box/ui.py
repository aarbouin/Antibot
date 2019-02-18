from typing import List

from antibot.model.user import User
from antibot.plugins.box.actions import OrderAction, PointsAction
from antibot.plugins.box.menu.model import Menu
from antibot.plugins.box.orders import Order
from antibot.slack.message import Option, Action, Attachment, OptionGroup, ActionStyle, Confirmation


class BoxUi:
    def create_order_attachments(self, menu: Menu, order: Order) -> List[Attachment]:
        options = [Option(box.name, repr(box)) for box in menu.boxes]
        add_box_action = Action.select(OrderAction.add_box, 'Pick a box...', options)
        clear_box_action = Action.button(OrderAction.clear_box, 'Clear boxes', 'clear_box')
        box_attachment = Attachment('update_order_{}'.format(order._id),
                                    actions=[add_box_action, clear_box_action],
                                    text='Add a box')

        options = []
        generic_group = []
        for dessert in menu.desserts:
            if len(dessert.flavors) > 0:
                values = [Option(str(df), repr(df)) for df in dessert.iter_flavors()]
                group = OptionGroup(dessert.name, values)
                options.append(group)
            else:
                df = dessert.with_flavor(None)
                generic_group.append(Option(str(df), repr(df)))

        options.insert(0, OptionGroup('Simple Desserts', generic_group))
        add_dessert_action = Action.group_select(OrderAction.add_dessert, 'Pick a dessert...', options)
        clear_dessert_action = Action.button(OrderAction.clear_dessert, 'Clear desserts', 'clear_dessert')
        dessert_attachment = Attachment('update_order_{}'.format(order._id),
                                        actions=[add_dessert_action, clear_dessert_action],
                                        text='Add a dessert')

        add_soup_action = Action.button(OrderAction.add_soup, 'Take a Soup', 'add_soup')
        options = [Option(drink.name, repr(drink)) for drink in menu.drinks]
        add_drink_action = Action.select(OrderAction.add_drink, 'Have a drink...', options)
        clear_others_action = Action.button(OrderAction.clear_others, 'Clear others', 'clear_others')
        others_attachment = Attachment('update_order_{}'.format(order._id),
                                       actions=[add_soup_action, add_drink_action, clear_others_action],
                                       text='Other options')

        validate_button = Action.button(OrderAction.order_confirm, 'Validate', 'order_confirm', ActionStyle.primary)
        cancel_button = Action.button(OrderAction.order_cancel, 'Cancel', 'order_cancel', ActionStyle.danger)
        edit_button = Action.button(OrderAction.order_edit, 'Modify', 'order_edit', ActionStyle.default)
        cancel_button_confirm = Action.button(OrderAction.order_cancel, 'Cancel', 'order_cancel', ActionStyle.danger,
                                              confirm=Confirmation('Really ?'))
        dismiss_button = Action.button(OrderAction.dismiss, 'Dismiss', 'dismiss')
        main_actions = []
        if not order.in_edition:
            main_actions.append(edit_button)
        else:
            main_actions.append(validate_button)
        if order.complete:
            main_actions.append(cancel_button_confirm)
        else:
            main_actions.append(cancel_button)
        main_actions.append(dismiss_button)
        main_attachment = Attachment('update_order_{}'.format(order._id),
                                     actions=main_actions,
                                     fallback='Order actions',
                                     color='warning' if order.in_edition else 'good')
        attachments = [main_attachment]
        if order.in_edition:
            attachments.extend([box_attachment, dessert_attachment, others_attachment])
        return attachments

    def orders_text(self, orders: List[Order]) -> str:
        messages = []
        total_box = 0
        for order in orders:
            text = '*{}*\n'.format(order.user.display_name)
            text += ''.join(['• {}\n'.format(item) for item in order.all_items()])
            total_box += len(order.boxes)
            messages.append(text)
        message = '----------\n'.join(messages)
        return message

    def create_points_attachment(self, pref_user: User) -> List[Attachment]:
        free_box_button = Action.button(PointsAction.free_box, 'Give a free box', 'free_box', ActionStyle.primary,
                                        confirm=Confirmation(
                                            text='Give a free box to {}'.format(pref_user.display_name),
                                            title='Free Box'
                                        ))
        dismiss_button = Action.button(PointsAction.dismiss, 'Dismiss', 'dismiss')

        attachment = Attachment('points_actions', actions=[free_box_button, dismiss_button], fallback='Free box')
        return [attachment]
