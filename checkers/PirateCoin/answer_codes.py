OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110


class CheckerAnswers:
    @staticmethod
    def OK(flag_id=""):  # require flag id only on put action!
        return CheckerAnswers.__return_answer(
            OK, flag_id=flag_id)

    @staticmethod
    def CORRUPT(public_message, private_message):
        return CheckerAnswers.__return_answer(
            CORRUPT, public_message, private_message)

    @staticmethod
    def MUMBLE(public_message, private_message):
        return CheckerAnswers.__return_answer(
            MUMBLE, public_message, private_message)

    @staticmethod
    def DOWN(public_message, private_message):
        return CheckerAnswers.__return_answer(
            DOWN, public_message, private_message)

    @staticmethod
    def CHECKER_ERROR(public_message, private_message):  # equals to 104 (DOWN)
        return CheckerAnswers.__return_answer(
            CHECKER_ERROR, public_message, private_message
        )

    @staticmethod
    def __return_answer(code, public_message="", private_message="", flag_id=""):
        return {
            "code": code,
            "public": public_message,
            "private": private_message,
            "flag_id": flag_id
        }
