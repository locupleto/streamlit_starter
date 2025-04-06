# ============================================================================
# -*- coding: utf-8 -*-
#
# Module:       base_page.py
# Description:  Defines the BasePage abstract base class that all pages must
#               inherit from. This ensures that each page implements the
#               required methods for displaying content, and providing
#               label, icon, and order for the menu.
#
# Mandatory Methods:
#   show_page(self): Display the content of the page.
#   label(self): Return the label for the page to be shown in the menu.
#   icon(self): Return the icon for the page to be shown in the menu.
#   order(self): Return the order in which the page should appear in the menu.
#
# History:
# 2024-05-18    urot  Created
# ============================================================================

from abc import ABC, abstractmethod

class BasePage(ABC):

    @abstractmethod
    def show_page(self):
        """Display the content of the page."""
        pass

    @abstractmethod
    def label(self):
        """Return the label for the page to be shown in the menu."""
        pass

    @abstractmethod
    def icon(self):
        """Return the icon for the page to be shown in the menu."""
        pass

    @abstractmethod
    def order(self):
        """Return the order in which the page should appear in the menu."""
        pass

