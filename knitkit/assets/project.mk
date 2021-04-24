base_dir=$(abspath .)

export MILL_LIB=$(base_dir)/{mill_lib_path}
export COURSIER_CACHE=$(base_dir)/{mill_cache_path}

MILL_BIN=$(base_dir)/{mill_path}
verilog:
	chmod +x $(MILL_BIN)
	cd $(base_dir)/hw/knitkit && $(MILL_BIN) knitkit.run $(base_dir)/builds
