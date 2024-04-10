import sys, os
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

IGNORED_EXCEPTIONS=(NoSuchElementException,StaleElementReferenceException,)

#Firefox does not understand how to scroll automatically to objects we want to put the mouse cursor over.
#Thus, we have to do it for it.
def scroll_shim(passed_in_driver, object):
    x = object.location['x']
    y = object.location['y']
    scroll_by_coord = 'window.scrollTo(%s,%s);' % (
        x,
        y
    )
    passed_in_driver.execute_script(scroll_by_coord)

#The program sometimes runs too fast for its own good. Make it try again if it can't find the popup.
def move_to_popup_and_get_authors(driver,popup):
    ActionChains(driver).move_to_element(popup).perform()
    popup = WebDriverWait(driver,10,ignored_exceptions=IGNORED_EXCEPTIONS).until(EC.presence_of_element_located((By.XPATH,"//div[contains(concat(' ', @class, ' '), ' MuiTooltip-popper ')]/div")))
    return [el.get_attribute("innerHTML") for el in popup.find_elements(By.XPATH,".//div/div/a")]

#Get attributions for portraits of a certain mon-form combination
def get_portrait_attributions(driver,pokemon_name="",pokemon_form_name=""): #Don't call this on its own.

    portraits_path = "//div[contains(concat(' ', @class, ' '), ' MuiContainer-root ')]/div[2]/div[1]"
    assert driver.find_element(By.XPATH,portraits_path+"/div/div/h5").get_attribute("innerHTML") == "Portraits", "Pathing to portraits failed."

    try:
        driver.find_element(By.XPATH,portraits_path+"/h5")
        print(f"No portraits in Repo for {pokemon_name} {pokemon_form_name}.",file=sys.stderr)
        return ""
    except NoSuchElementException:
        #We don't actually need to do anything here because if this element doesn't exist, good.
        pass

    portrait_objects = driver.find_elements(By.XPATH, portraits_path+"/div[2]/div[contains(concat(' ', @class, ' '), ' MuiGrid-item ')]/div/div")

    portraits = []
    for portrait in portrait_objects:
        portrait_name = portrait.find_element(By.XPATH, ".//p").get_attribute("innerHTML")
        portrait_hover = portrait.find_element(By.XPATH, ".//*[name()='svg']")
        for _ in range(10):
            try:
                portrait_authors = move_to_popup_and_get_authors(driver,portrait_hover)
                break
            except StaleElementReferenceException:
                print("pass failed with StaleElementReferenceException")
        if "CHUNSOFT" in portrait_authors: portrait_authors = ["CHUNSOFT"]
        portraits.append([portrait_name,portrait_authors])

    return portraits

#Get attributions for sprites of a certain mon-form combination
def get_sprite_attributions(driver,pokemon_name="",pokemon_form_name=""): #Don't call this on its own.
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
    sprites_path = "//div[contains(concat(' ', @class, ' '), ' MuiContainer-root ')]/div[2]/div[2]"
    assert driver.find_element(By.XPATH,sprites_path+"/div/div/h5").get_attribute("innerHTML") == "Sprites", "Pathing to sprites failed."
    try:
        driver.find_element(By.XPATH,sprites_path+"/h6")
        print(f"No sprites in Repo for {pokemon_name} {pokemon_form_name}.",file=sys.stderr)
        return ''
    except NoSuchElementException:
        #We don't actually need to do anything here because if this element doesn't exist, good.
        pass
    sprite_objects = driver.find_elements(By.XPATH, sprites_path+"/div[2]/div[contains(concat(' ', @class, ' '), ' MuiGrid-item ')]/div/div/div[2]")

    sprites = []
    for sprite in sprite_objects:
        sprite_name = sprite.find_element(By.XPATH, ".//p").get_attribute("innerHTML")
        sprite_hover = sprite.find_element(By.XPATH, ".//*[name()='svg']")
        scroll_shim(driver,sprite_hover) #Fix MoveTargetOutOfBoundsException
        for _ in range(10):
            try:
                sprite_authors = move_to_popup_and_get_authors(driver,sprite_hover)
                break
            except StaleElementReferenceException:
                print("pass failed with StaleElementReferenceException")
        if "CHUNSOFT" in sprite_authors: sprite_authors = ["CHUNSOFT"]
        sprites.append([sprite_name,sprite_authors])

    return sprites

#Get all attributions for a certain mon-form combination.
#Mon should be specified by pokedex number, form by name in lowercase.
def get_pokemon_attributions_from_dex_number_and_form(driver,mon_number,form): #Call this.
    driver.get(f"https://sprites.pmdcollab.org/#/{mon_number}")
    assert 'PMD Sprite Repository' in driver.title

    try:
        driver.find_element(By.XPATH,"//div[@id='root']/div/h1")
        print(f"Pokemon with dex number {mon_number} does not exist in repo.",file=sys.stderr)
        return ''
    except NoSuchElementException:
        #We don't actually need to do anything here because if this element doesn't exist, good.
        pass

    header_path = "//div[contains(concat(' ', @class, ' '), ' MuiContainer-root ')]/div[1]/div[2]/div"
    forms_button_path = header_path + "/div[contains(concat(' ', @class, ' '), ' MuiInputBase-root ')]"

    #pokemon_name = WebDriverWait(driver, 10, ignored_exceptions=IGNORED_EXCEPTIONS).until(EC.presence_of_element_located((By.XPATH,header_path+"/h5"))).get_attribute("innerHTML")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,forms_button_path))).click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,"//div[@id='menu-']")))
    pokemon_forms = [el.get_attribute("innerHTML") for el in driver.find_elements(By.XPATH,"//div[@id='menu-']/div[3]/ul/li/h6")]
    driver.find_element(By.XPATH,f"//div[@id='menu-']/div[3]/ul/li/h6").click()

    pokemon_forms = {k.lower():v for v,k in enumerate(pokemon_forms)}

    try:
        form_number = pokemon_forms[form]
    except KeyError as e:
        raise ValueError(f"Form {form} does not exist for pokemon with dex number {mon_number}!")
    driver.get(f"https://sprites.pmdcollab.org/#/{mon_number}?form={form_number}")

    pokemon_name = driver.find_element(By.XPATH,header_path+"/h5").get_attribute("innerHTML")
    pokemon_form_name = driver.find_element(By.XPATH,forms_button_path+"/div/h6").get_attribute("innerHTML")
    assert form == pokemon_form_name.lower(), "Pokemon form in repo not equivalent to entered Pokemon form."
    assert mon_number in pokemon_name, "Pokedex number in repo not equivalent to entered Pokedex number."

    portraits = get_portrait_attributions(driver,pokemon_name,pokemon_form_name)
    sprites = get_sprite_attributions(driver,pokemon_name,pokemon_form_name)

    portrait_attributions = []
    for portrait_name,authors in portraits:
        authors = ", ".join(set(authors))
        portrait_attributions.append(f"{pokemon_name} {pokemon_form_name} {portrait_name} by {authors}, {'licensed under a proprietary license.' if authors == 'CHUNSOFT' else 'licensed under CC-BY-NC-4.0.'}")

    sprite_attributions = []
    for sprite_name,authors in sprites:
        authors = ", ".join(set(authors))
        sprite_attributions.append(f"{pokemon_name} {pokemon_form_name} {sprite_name} by {authors}, {'licensed under a proprietary license.' if authors == 'CHUNSOFT' else 'licensed under CC-BY-NC-4.0.'}")

    return "\n".join(portrait_attributions+sprite_attributions)

if __name__ == "__main__":
    try:
        #os.environ['MOZ_HEADLESS'] = '1'
        driver = webdriver.Firefox()

        with open("input.txt",encoding="utf-8") as file:
            mons = [(l[0].rjust(4,"0"),'normal' if len(l)==1 else l[1].lower().strip()) for l in [l.split(",") for l in file.read().splitlines()]]
        
        attributions = ""
        for mon, form in tqdm(mons):
            attributions += get_pokemon_attributions_from_dex_number_and_form(driver,mon,form) + "\n"
        
        with open("output.txt",mode="w",encoding="utf-8") as file:
            file.write(attributions)
        driver.quit()
    except Exception as e:
        driver.quit()
        raise e