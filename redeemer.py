from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
from loguru import logger
import sys
from config import load_config
import random


async def main():
    config = load_config()
    options = webdriver.ChromeOptions()
    window_size = config["options"].get(
        "window_size", {"width": 1280, "height": 720})
    options.add_argument(
        f"--window-size={window_size['width']},{window_size['height']}")

    async with webdriver.Chrome(options=options) as driver:
        await driver.get('https://profile.callofduty.com/cod/login', wait_load=True)
        await driver.sleep(0.5)
        logger.info("Please login to your CoD Account")
        logger.info("Fill in your email + password and complete the reCAPTCHA")
        logger.info("Once done, hit the SIGN IN button")

        while True:
            current_url = await driver.current_url
            if current_url == "https://profile.callofduty.com/cod/profile":
                logger.info("Successfully logged in!")
                break
            await asyncio.sleep(2)

        logger.info("Starting Redeemer")
        codes_redeemed = 0

        with open("codes.txt", "r") as f:
            codes = f.readlines()
            for code in codes:
                if codes_redeemed >= config["options"]["redeem_limit_max"]:
                    logger.warning("Reached maximum redeem limit!")
                    break

                code = code.strip()
                success = False
                while not success:
                    await driver.get('https://profile.callofduty.com/promotions/redeemCode', wait_load=True)

                    delay = random.uniform(
                        config["options"]["min_delay_ms"] / 1000, config["options"]["max_delay_ms"] / 1000)
                    await driver.sleep(delay)

                    code_input = await driver.find_element(By.XPATH, '//*[@id="code"]', timeout=15)
                    redeem_button = await driver.find_element(By.XPATH, '//*[@id="redeem-code-button"]', timeout=15)
                    await code_input.send_keys(code)
                    await redeem_button.click()
                    await driver.sleep(1)

                    try:
                        ratelimit_message = await driver.find_element(
                            By.XPATH,
                            '//*[@id="redemptionForm"]/fieldset/section/section/p',
                            timeout=2
                        )
                        if ratelimit_message:
                            logger.error(
                                f"Rate-limited, waiting 30 seconds before trying code: {code} again")
                            await driver.sleep(30)
                            # Redeem code when not ratelimited (hopefully)
                            continue
                    except:
                        try:
                            thanks_message = await driver.find_element(
                                By.XPATH,
                                '/html/body/section[1]/main/section/p[1]',
                                timeout=25
                            )
                            if thanks_message:
                                logger.info(f"Redeemed code: {code}")
                                codes_redeemed += 1
                                success = True
                        except:
                            logger.error(f"Failed to redeem code: {code}")
                            # Move to next code even if failed (never happened before but just in case)
                            success = True

            logger.success(f"Redeemed {codes_redeemed} codes!")


if __name__ == "__main__":
    logger.remove()
    logger.add(
        sys.stderr, format="<green>{time:HH:mm:ss}</green> | {level} | {message}")

    asyncio.run(main())
