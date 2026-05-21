import unittest

from handsome_bench import expand_roster, is_truncated_response, parse_score


class ParseScoreTests(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(parse_score("87"), 87)

    def test_decimal(self):
        self.assertEqual(parse_score("92.75"), 92.75)

    def test_extra_text(self):
        self.assertEqual(parse_score("You are 88.5/100."), 88.5)

    def test_out_of_range(self):
        self.assertIsNone(parse_score("101"))
        self.assertIsNone(parse_score("0.5"))

    def test_no_number(self):
        self.assertIsNone(parse_score("handsome"))


class RosterTests(unittest.TestCase):
    def test_reasoning_configs_are_medium_or_higher(self):
        configs = expand_roster()
        forbidden = {"none", "low", "minimal", 0, -1, False}
        for config in configs:
            self.assertNotIn(config.reasoning_value, forbidden)

    def test_has_expanded_base_model_count(self):
        providers_and_models = {(spec.provider, spec.model) for spec in __import__("handsome_bench").ROSTER}
        self.assertGreaterEqual(len(providers_and_models), 30)


class TruncationTests(unittest.TestCase):
    def test_gemini_max_tokens_is_truncated(self):
        data = {"candidates": [{"finishReason": "MAX_TOKENS"}]}
        self.assertTrue(is_truncated_response("google", data))

    def test_gemini_stop_is_not_truncated(self):
        data = {"candidates": [{"finishReason": "STOP"}]}
        self.assertFalse(is_truncated_response("google", data))

    def test_anthropic_max_tokens_is_truncated(self):
        self.assertTrue(is_truncated_response("anthropic", {"stop_reason": "max_tokens"}))

    def test_openai_compatible_length_is_truncated(self):
        data = {"choices": [{"finish_reason": "length"}]}
        self.assertTrue(is_truncated_response("dashscope", data))


if __name__ == "__main__":
    unittest.main()
