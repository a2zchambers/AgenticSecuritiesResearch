import logging

logger = logging.getLogger(__name__)

def apply_framework_monkey_patches():
    """
    Dynamically intercepts and overrides internal model parsing functions 
    inside tradingagents to allow direct dictionary configuration structures.
    """
    try:
        # Import the model provider target module directly from the repository layout
        import tradingagents.llms.model_provider as mp
        
        # Check if original function exists and back it up
        if hasattr(mp, 'get_model') and not hasattr(mp, '_patched_by_a2z'):
            original_get_model = mp.get_model
            
            def patched_get_model(model_config, *args, **kwargs):
                """Safely handles config targets whether they are dict profiles or strings."""
                # If the repository code tries to call .lower() on a dictionary configuration payload
                if isinstance(model_config, dict):
                    # Extract the raw string name so its internal string searches succeed
                    model_str = model_config.get("model", "qwen2.5:7b")
                    logger.info(f"[A2Z Patch] Intercepted dict config. Mapping model name: {model_str}")
                    return original_get_model(model_str, *args, **kwargs)
                
                return original_get_model(model_config, *args, **kwargs)
            
            # Apply patch handles
            mp.get_model = patched_get_model
            mp._patched_by_a2z = True
            print("[Patch Engine] Successfully patched tradingagents model provider schema handlers.")
            
    except Exception as e:
        print(f"[Patch Engine Warning] Non-critical monkey-patch binding failed: {str(e)}")

# Apply the patch immediately upon import evaluation
apply_framework_monkey_patches()
