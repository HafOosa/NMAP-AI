def load_hard_agent(self):
    """Charge Hard Generator"""
    if 'hard' in self._agents_cache:
        return self._agents_cache['hard']
    
    # Setup paths
    models_root = self.project_root / "AgentModels"
    agents_dir = models_root / "agents"
    
    self._add_to_path(self.project_root, models_root, agents_dir)
    
    try:
        import importlib.util
        
        # ✅ NOUVEAU NOM : generator_hard_agent.py
        hard_path = agents_dir / "generator_hard_agent.py"
        
        if not hard_path.exists():
            raise FileNotFoundError(f"generator_hard_agent.py not found in {agents_dir}")
        
        spec = importlib.util.spec_from_file_location("generator_hard_agent", hard_path)
        hard_module = importlib.util.module_from_spec(spec)
        sys.modules['generator_hard_agent'] = hard_module
        spec.loader.exec_module(hard_module)
        
        self._agents_cache['hard'] = hard_module
        return hard_module
        
    except Exception as e:
        print(f"Error loading Hard agent: {e}")
        import traceback
        traceback.print_exc()
        return None