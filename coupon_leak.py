from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Create a new instance of the Edge driver
driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
 
driver.get("https://courson.xyz/coupons")

# Validate the title
expected_title = "Live 100% off"
actual_title = driver.title

Loadmore_xpath = '//*[@id="load-more"]'

if expected_title in actual_title:
    print("Title validation successful!")
else:
    print("Title validation failed. Expected:", expected_title, "Actual:", actual_title)

# Get all <a> elements within the div with the specified XPath
div_element = driver.find_element("xpath", '//*[@id="coupons-container"]')
a_elements = div_element.find_elements("tag name", "a")

# Access each link and get the href of the specified link within each page
course_links = []
for a in a_elements:
    course_links.append(a.get_attribute("href"))

claim_links = []
for link in course_links:
    driver.get(link)
    inner_link_element = driver.find_element("xpath", '/html/body/div/div/div/div[4]/div[1]/div/a')
    claim_links.append(inner_link_element.get_attribute("href"))
# print("coupons:" + inner_link_href)
    # print("coupons:" + inner_link_href)

course_info = []
for link in claim_links:
    print(f"[[INFO]] Processing link: {link}")
    driver.get(link)
    try:
        coupon_code_element = driver.find_element("xpath", '//*[@id="couponCode"]')
        coupon_code = coupon_code_element.text
        inner_link_element = driver.find_element("xpath", '/html/body/div/div/div[2]/div[2]/a')
        inner_link_href = inner_link_element.get_attribute("href")
        course_info.append((coupon_code, inner_link_href))
    except:
        print(f"[[ERROR]] Coupon code not found for link: {link}")
        pass

# Loop through the list to print out the information
for info in course_info:
    print("Coupon Code:", info[0])
    print("Link:", info[1])# Close the browser
driver.quit()




# Close the browser
driver.quit()


# Close the browser
driver.quit()

