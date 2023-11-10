from selenium.webdriver.common.action_chains import ActionChains

# Define a list of user actions
actions = [
    "open_url",             # Open a URL
    "click_element",        # Click on an element
    "scroll_page",          # Scroll the page
    "type_text",            # Type text into an input field
    "hover_element",        # Hover over an element
    "double_click_element", # Double-click on an element
    "right_click_element",  # Right-click on an element
    "go_back",              # Navigate back in the browser
    "go_forward",           # Navigate forward in the browser
    "refresh_page"          # Refresh the page
]

# Define a function for each action
class Actions:
    def open_url(self, url):
        self.driver.get(url)

    def click_element(self, selector):
        element = self.driver.find_element_by_css_selector(selector)
        element.click()

    def scroll_page(self, direction="down", pixels=300):
        if direction == "down":
            self.driver.execute_script(f"window.scrollBy(0, {pixels});")
        elif direction == "up":
            self.driver.execute_script(f"window.scrollBy(0, -{pixels});")

    def type_text(self, selector, text):
        element = self.driver.find_element_by_css_selector(selector)
        element.send_keys(text)

    def hover_element(self, selector):
        element = self.driver.find_element_by_css_selector(selector)
        ActionChains(self.driver).move_to_element(element).perform()

    def double_click_element(self, selector):
        element = self.driver.find_element_by_css_selector(selector)
        ActionChains(self.driver).double_click(element).perform()

    def right_click_element(self, selector):
        element = self.driver.find_element_by_css_selector(selector)
        ActionChains(self.driver).context_click(element).perform()

    def go_back(self):
        self.driver.back()

    def go_forward(self):
        self.driver.forward()

    def refresh_page(self):
        self.driver.refresh()

# Perform actions
actions_to_perform = [
    "open_url('https://example.com')",
    "click_element('.button-class')",
    "scroll_page('down', 200)",
    "type_text('.search-input', 'Selenium')",
    "hover_element('.menu-item')",
    "double_click_element('.double-clickable-element')",
    "right_click_element('.context-menu-element')",
    "go_back()",
    "go_forward()",
    "refresh_page()"
]

# for action in actions_to_perform:
#     eval(action)
#     time.sleep(2)  # Add a delay between actions to make it more human-like

