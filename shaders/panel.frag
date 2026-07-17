#version 330 core
in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D u_camera_texture;
uniform float u_time;
uniform int u_draw_border; // 1 if drawing white border, 0 for texture
uniform vec2 u_resolution;
uniform int u_effect_mode; // Modes 0 to 9
uniform float u_glitch_factor; // Glitch amount (1.0 down to 0.0) during transition

// Pseudo-random noise
float random(vec2 st) {
    return fract(sin(dot(st, vec2(12.9898, 78.233))) * 43758.5453123);
}

// Rotated halftone pattern — returns dot intensity at a given angle
float halftone(vec2 pixel, float angle, float dot_size, float brightness) {
    float s = sin(angle);
    float c = cos(angle);
    vec2 rotated = vec2(
        pixel.x * c - pixel.y * s,
        pixel.x * s + pixel.y * c
    );
    
    vec2 cell = floor(rotated / dot_size);
    vec2 center = (cell + 0.5) * dot_size;
    
    float max_r = dot_size * 0.55;
    float radius = (1.0 - brightness) * max_r;
    
    float dist = distance(rotated, center);
    return smoothstep(radius + 0.8, radius - 0.8, dist);
}

// Simple Sobel edge detection
float edge_detect(vec2 uv, vec2 texel) {
    float tl = dot(texture(u_camera_texture, uv + vec2(-texel.x, texel.y)).rgb, vec3(0.299, 0.587, 0.114));
    float t  = dot(texture(u_camera_texture, uv + vec2(0.0, texel.y)).rgb, vec3(0.299, 0.587, 0.114));
    float tr = dot(texture(u_camera_texture, uv + vec2(texel.x, texel.y)).rgb, vec3(0.299, 0.587, 0.114));
    float l  = dot(texture(u_camera_texture, uv + vec2(-texel.x, 0.0)).rgb, vec3(0.299, 0.587, 0.114));
    float r  = dot(texture(u_camera_texture, uv + vec2(texel.x, 0.0)).rgb, vec3(0.299, 0.587, 0.114));
    float bl = dot(texture(u_camera_texture, uv + vec2(-texel.x, -texel.y)).rgb, vec3(0.299, 0.587, 0.114));
    float b  = dot(texture(u_camera_texture, uv + vec2(0.0, -texel.y)).rgb, vec3(0.299, 0.587, 0.114));
    float br = dot(texture(u_camera_texture, uv + vec2(texel.x, -texel.y)).rgb, vec3(0.299, 0.587, 0.114));
    
    float gx = -tl - 2.0*l - bl + tr + 2.0*r + br;
    float gy = -tl - 2.0*t - tr + bl + 2.0*b + br;
    
    return sqrt(gx * gx + gy * gy);
}

void main()
{
    if (u_draw_border == 1) {
        vec4 border_col;
        // Colored border depending on selected mode (0 to 9)
        if (u_effect_mode == 0) {
            border_col = vec4(1.0, 1.0, 1.0, 1.0); // White
        } else if (u_effect_mode == 1) {
            border_col = vec4(0.0, 0.85, 1.0, 1.0); // Neon Cyan
        } else if (u_effect_mode == 2) {
            border_col = vec4(0.0, 1.0, 0.3, 1.0); // Matrix Green
        } else if (u_effect_mode == 3) {
            border_col = vec4(0.88, 0.07, 0.08, 1.0); // Spider-Man Red
        } else if (u_effect_mode == 4) {
            border_col = vec4(1.0, 0.0, 1.0, 1.0); // Cyber Magenta
        } else if (u_effect_mode == 5) {
            border_col = vec4(0.12, 0.22, 0.95, 1.0); // Miles Blue
        } else if (u_effect_mode == 6) {
            border_col = vec4(0.1, 0.1, 0.1, 1.0); // Ink Charcoal
        } else if (u_effect_mode == 7) {
            border_col = vec4(1.0, 0.05, 0.75, 1.0); // Dimension Magenta
        } else if (u_effect_mode == 8) {
            border_col = vec4(1.0, 0.55, 0.72, 1.0); // Anime Sakura Pink
        } else {
            border_col = vec4(0.60, 0.04, 0.04, 1.0); // Vintage Comic Red
        }

        if (u_glitch_factor > 0.0) {
            // Glitch border: flicker color between original and bright dimension cyan/magenta
            float flip = step(0.5, random(vec2(u_time * 10.0, gl_FragCoord.y)));
            vec4 glitch_color = mix(vec4(0.05, 0.88, 1.0, 1.0), vec4(1.0, 0.04, 0.78, 1.0), flip);
            FragColor = mix(border_col, glitch_color, u_glitch_factor * 0.75);
        } else {
            FragColor = border_col;
        }
        return;
    }

    // Screen-space UV for camera sampling
    vec2 screen_uv = gl_FragCoord.xy / u_resolution;
    screen_uv.y = 1.0 - screen_uv.y;
    
    // Apply digital screen tearing and scanline wave shake during transition glitch
    if (u_glitch_factor > 0.0) {
        // Horizontal tearing line displacement
        float tear = step(0.95 - 0.03 * sin(u_time * 60.0), sin(screen_uv.y * 35.0 + u_time * 20.0));
        screen_uv.x += (random(vec2(floor(screen_uv.y * 30.0), u_time)) - 0.5) * 0.04 * u_glitch_factor * tear;
        
        // Scanline high-frequency wave shake
        screen_uv.x += sin(screen_uv.y * 140.0 + u_time * 45.0) * 0.006 * u_glitch_factor;
    }
    
    vec3 cam_color;
    if (u_glitch_factor > 0.0) {
        // Chromatic aberration channel split (Cyan / Magenta fringes)
        float shift = 0.018 * u_glitch_factor;
        float r = texture(u_camera_texture, screen_uv + vec2(shift, 0.0)).r;
        float g = texture(u_camera_texture, screen_uv).g;
        float b = texture(u_camera_texture, screen_uv - vec2(shift, 0.0)).b;
        cam_color = vec3(r, g, b);
    } else {
        cam_color = texture(u_camera_texture, screen_uv).rgb;
    }
    
    float gray = dot(cam_color, vec3(0.299, 0.587, 0.114));
    
    vec3 final_color = vec3(0.0);
    vec2 pixel = gl_FragCoord.xy;
    vec2 texel = 1.0 / u_resolution;
    
    if (u_effect_mode == 0) {
        // ==================== MODE 0: RED RISO HALFTONE ====================
        vec3 cream_paper = vec3(0.97, 0.95, 0.90);
        vec3 riso_red    = vec3(0.85, 0.12, 0.15);
        vec3 dark_charcoal = vec3(0.08, 0.08, 0.10);
        
        float red_dots = halftone(pixel, radians(45.0), 10.0, gray);
        final_color = mix(cream_paper, riso_red, red_dots * 0.95);
        
        float edges = edge_detect(screen_uv, texel * 2.0);
        float edge_mask = smoothstep(0.15, 0.4, edges);
        final_color = mix(final_color, dark_charcoal, edge_mask * 0.8);
    }
    else if (u_effect_mode == 1) {
        // ==================== MODE 1: BLUE BLUEPRINT ====================
        vec3 deep_navy = vec3(0.03, 0.06, 0.20);
        vec3 bright_cyan = vec3(0.0, 0.85, 1.0);
        vec3 blueprint_white = vec3(0.90, 0.95, 1.0);
        
        float grid_sz = 16.0;
        vec2 grid = abs(fract(pixel / grid_sz) - 0.5) / fwidth(pixel / grid_sz);
        float grid_line = min(grid.x, grid.y);
        float is_grid = 1.0 - smoothstep(0.0, 1.5, grid_line);
        
        vec3 duotone = mix(deep_navy, bright_cyan, gray);
        final_color = mix(duotone, blueprint_white, is_grid * 0.15);
        
        float edges = edge_detect(screen_uv, texel * 2.0);
        float edge_mask = smoothstep(0.15, 0.4, edges);
        final_color = mix(final_color, bright_cyan, edge_mask * 0.9);
    }
    else if (u_effect_mode == 2) {
        // ==================== MODE 2: GREEN DIGITAL MATRIX ====================
        vec3 matrix_bg = vec3(0.01, 0.03, 0.01);
        vec3 neon_green = vec3(0.0, 1.0, 0.3);
        
        float scanline = sin(pixel.y * 0.5 - u_time * 10.0) * 0.5 + 0.5;
        vec2 pixelated_uv = floor(screen_uv * vec2(160.0, 90.0)) / vec2(160.0, 90.0);
        float px_gray = dot(texture(u_camera_texture, pixelated_uv).rgb, vec3(0.299, 0.587, 0.114));
        
        vec2 cell = fract(pixel / 8.0) - 0.5;
        float dot_pat = smoothstep(0.4, 0.3, length(cell));
        
        vec3 matrix_fg = neon_green * px_gray * (0.6 + 0.4 * scanline);
        final_color = mix(matrix_bg, matrix_fg, dot_pat);
        
        float edges = edge_detect(screen_uv, texel * 2.0);
        float edge_mask = smoothstep(0.15, 0.4, edges);
        final_color = mix(final_color, neon_green, edge_mask * 0.9);
    }
    else if (u_effect_mode == 3) {
        // ==================== MODE 3: SPIDER-VERSE — BEN-DAY DOTS + CMYK MIS-REGISTRATION ====================
        vec3 sp_red    = vec3(0.88, 0.07, 0.08);
        vec3 sp_blue   = vec3(0.05, 0.15, 0.88);
        vec3 sp_yellow = vec3(0.98, 0.86, 0.04);
        vec3 sp_black  = vec3(0.04, 0.03, 0.06);
        vec3 sp_white  = vec3(0.97, 0.94, 0.88);
        
        // CMYK mis-registration: sample R and B from offset UVs (old offset printing error)
        float mis = 0.004;
        float r_lum = dot(texture(u_camera_texture, screen_uv + vec2(mis, 0.0)).rgb,  vec3(0.299, 0.587, 0.114));
        float b_lum = dot(texture(u_camera_texture, screen_uv + vec2(-mis, mis)).rgb, vec3(0.299, 0.587, 0.114));
        
        // Ben-Day dots: uniform fixed-size grid (classic comic printing)
        float dot_sz = 8.0;
        vec2 bd_cell   = floor(pixel / dot_sz);
        vec2 bd_center = (bd_cell + 0.5) * dot_sz;
        float bd_dist  = distance(pixel, bd_center);
        float bd_r     = dot_sz * 0.42;
        float ben_dot  = smoothstep(bd_r + 0.9, bd_r - 0.9, bd_dist);
        
        // Map brightness zones to Spider-Verse palette
        vec3 sp_base;
        if (gray < 0.22) {
            sp_base = sp_black;
        } else if (gray < 0.52) {
            sp_base = mix(sp_black, sp_red, ben_dot);
        } else if (gray < 0.78) {
            sp_base = mix(sp_red, sp_yellow, ben_dot);
        } else {
            sp_base = mix(sp_yellow, sp_white, ben_dot);
        }
        
        // CMYK color bleed: cyan fringe on red channel mismatch
        float bleed = abs(r_lum - b_lum) * 3.5;
        sp_base = mix(sp_base, sp_blue * 0.65 + sp_red * 0.35, clamp(bleed * 0.45, 0.0, 0.4));
        
        // Strong ink outline (Spider-Verse thick inking)
        float edges3 = edge_detect(screen_uv, texel * 2.0);
        float edge_mask3 = smoothstep(0.13, 0.32, edges3);
        final_color = mix(sp_base, sp_black, edge_mask3 * 0.97);
    }
    else if (u_effect_mode == 4) {
        // ==================== MODE 4: MILES MORALES GLITCH (RED, BLUE & BLACK) ====================
        vec3 g_red   = vec3(0.90, 0.05, 0.08);   // Miles Spidey Red
        // Deep Miles neon blue
        vec3 g_blue  = vec3(0.04, 0.18, 0.95);   
        vec3 g_black = vec3(0.02, 0.01, 0.03);   // Ink black shadows
 
        vec2 uv = screen_uv;
        
        // Slice-tearing digital glitch
        float time_snap = floor(u_time * 12.0);
        float slice_y = floor(uv.y * 20.0);
        float slice_noise = random(vec2(slice_y, time_snap));
        if (slice_noise > 0.82) {
            uv.x += (random(vec2(time_snap, slice_y)) - 0.5) * 0.07;
        }
 
        // Horizontal scanline wave ripple
        float wave = sin(uv.y * 120.0 + u_time * 25.0) * 0.004;
        uv.x += wave;
 
        // Channel separation for Red and Blue (Green channel is forced to 0.0)
        float split_offset = 0.012 + 0.008 * sin(u_time * 6.0);
        float r_chan = texture(u_camera_texture, uv + vec2(split_offset, 0.0)).r;
        float b_chan = texture(u_camera_texture, uv - vec2(split_offset, 0.0)).b;
 
        // Apply Ben-Day dots overlay on Red channel
        float bd_sz = 6.0;
        vec2 bd_c = floor(pixel / bd_sz);
        vec2 bd_cn = (bd_c + 0.5) * bd_sz;
        float bd_d = distance(pixel, bd_cn);
        float dot_pat = smoothstep(bd_sz * 0.44 + 0.8, bd_sz * 0.44 - 0.8, bd_d);
 
        // Threshold values to create crisp graphic pop-art edges
        float r_mask = smoothstep(0.34, 0.44, r_chan);
        float b_mask = smoothstep(0.34, 0.44, b_chan);
 
        // Combine into red/blue/black palette
        vec3 glitch_base = g_black;
        glitch_base = mix(glitch_base, g_blue, b_mask);
        glitch_base = mix(glitch_base, g_red, r_mask * dot_pat); // Red mapped to halftone dots
 
        // Animate moving dark scanline bars
        float bar = sin(pixel.y * 0.2 - u_time * 15.0) * 0.5 + 0.5;
        glitch_base += vec3(bar * 0.12 * r_mask, 0.0, bar * 0.15 * b_mask);
 
        // Clip deep shadows back to solid black
        float org_gray = dot(texture(u_camera_texture, uv).rgb, vec3(0.299, 0.587, 0.114));
        if (org_gray < 0.15) {
            glitch_base = g_black;
        }
 
        // Thick comic black ink outline
        float edges4 = edge_detect(uv, texel * 2.5);
        float edge_mask4 = smoothstep(0.12, 0.32, edges4);
        final_color = mix(glitch_base, g_black, edge_mask4 * 0.99);
    }
    else if (u_effect_mode == 5) {
        // ==================== MODE 5: SPIDER-VERSE — CEL SHADING (MILES MORALES) ====================
        vec3 cel_black = vec3(0.05, 0.03, 0.08);  // deep shadow ink
        vec3 cel_red   = vec3(0.80, 0.07, 0.10);  // spider-red midtone
        vec3 cel_cream = vec3(0.96, 0.92, 0.84);  // highlight cream
        vec3 cel_blue  = vec3(0.10, 0.18, 0.90);  // Miles signature blue
        
        // Quantize to 4 hard flat levels (Cel / toon shading)
        float cel_level;
        if (gray < 0.20)      cel_level = 0.0;
        else if (gray < 0.45) cel_level = 0.33;
        else if (gray < 0.70) cel_level = 0.66;
        else                  cel_level = 1.0;
        
        vec3 cel_color;
        if (cel_level < 0.1) {
            cel_color = cel_black;
        } else if (cel_level < 0.45) {
            cel_color = cel_red;
        } else if (cel_level < 0.8) {
            cel_color = mix(cel_red, cel_cream, 0.45);
        } else {
            cel_color = cel_cream;
        }
        
        // Halftone dots in shadow zone (like Spider-Verse ink gradients)
        float shadow_ht = halftone(pixel, radians(45.0), 6.0, gray);
        if (gray < 0.48) {
            cel_color = mix(cel_black, cel_red, shadow_ht);
        }
        
        // Blue accent shimmer on bright areas (web-shooter glow)
        float bright_edge = smoothstep(0.68, 0.90, gray);
        cel_color = mix(cel_color, cel_blue * 0.3 + cel_cream * 0.7, bright_edge * 0.22);
        
        // Very thick ink-black outline
        float edges5 = edge_detect(screen_uv, texel * 2.0);
        float edge_mask5 = smoothstep(0.10, 0.28, edges5);
        final_color = mix(cel_color, cel_black, edge_mask5 * 0.98);
    }
    else if (u_effect_mode == 6) {
        // ==================== MODE 6: MANGA INK SKETCH ====================
        vec3 paper = vec3(0.95, 0.95, 0.93);
        vec3 ink = vec3(0.08, 0.08, 0.12);
        
        float hatch1 = fract((pixel.x + pixel.y) * 0.14);
        float hatch2 = fract((pixel.x - pixel.y) * 0.14);
        
        float draw_hatch = 0.0;
        if (gray < 0.60 && hatch1 < 0.15) {
            draw_hatch = 1.0;
        }
        if (gray < 0.35 && hatch2 < 0.15) {
            draw_hatch = 1.0;
        }
        if (gray < 0.15) {
            draw_hatch = 1.0;
        }
        
        final_color = mix(paper, ink, draw_hatch);
        
        float edges = edge_detect(screen_uv, texel * 2.0);
        float edge_mask = smoothstep(0.12, 0.3, edges);
        final_color = mix(final_color, ink, edge_mask * 0.95);
    }
    else if (u_effect_mode == 7) {
        // ==================== MODE 7: SPIDER-VERSE — GLITCH DIMENSION PORTAL ====================
        // Animated glitch bar (dimension tear)
        float glitch_seed = floor(u_time * 4.0);
        float glitch_y    = fract(sin(glitch_seed * 917.3 + 43.7) * 5831.9);
        float glitch_bar  = step(glitch_y, screen_uv.y) * step(screen_uv.y, glitch_y + 0.07);
        float glitch_bar2 = step(fract(glitch_y + 0.4), screen_uv.y) * step(screen_uv.y, fract(glitch_y + 0.4) + 0.03);
        float any_bar = max(glitch_bar, glitch_bar2);
        
        // Strong chromatic aberration (dimension-crossing color split)
        float chrom = 0.009 + any_bar * 0.018;
        float ang   = u_time * 2.2;
        vec2 r_off  = vec2( cos(ang),  sin(ang)) * chrom;
        vec2 b_off  = vec2(-cos(ang), -sin(ang)) * chrom * 1.6;
        
        float dim_r = texture(u_camera_texture, screen_uv + r_off).r;
        float dim_g = texture(u_camera_texture, screen_uv).g;
        float dim_b = texture(u_camera_texture, screen_uv + b_off).b;
        vec3 aberrated = vec3(dim_r, dim_g, dim_b);
        
        // Play Ben-Day dots overlay in dimension colors
        float bd_sz = 7.0;
        vec2 bd_c2   = floor(pixel / bd_sz);
        vec2 bd_cn2  = (bd_c2 + 0.5) * bd_sz;
        float bd_d2  = distance(pixel, bd_cn2);
        float bd_dot = smoothstep(bd_sz * 0.4 + 0.9, bd_sz * 0.4 - 0.9, bd_d2);
        
        // Dimension color palette: magenta / cyan alternating by cell
        float cell_alt = mod(bd_c2.x + bd_c2.y, 2.0);
        vec3 dim_col = mix(vec3(1.0, 0.04, 0.78), vec3(0.02, 0.88, 1.0), cell_alt);
        
        // Blend aberrated image with pulsing Ben-Day dimension dots
        float dot_pulse = 0.28 + 0.10 * sin(u_time * 3.5);
        final_color = mix(aberrated, dim_col, bd_dot * dot_pulse);
        
        // Glitch bar: color inversion + magenta wash (dimension tear)
        if (any_bar > 0.5) {
            final_color = mix(1.0 - final_color, vec3(0.95, 0.05, 0.80), 0.45);
        }
        
        // Subtle scanline distortion
        float scan7 = sin(pixel.y * 1.4) * 0.07 + 0.93;
        final_color *= scan7;
    }
    else if (u_effect_mode == 8) {
        // ==================== MODE 8: VIBRANT ANIME CEL-SHADING ====================
        // 1. Boost saturation and contrast for a colorful anime look
        vec3 sat_color = mix(vec3(gray), cam_color, 1.6);
        sat_color = clamp(sat_color * 1.15 - vec3(0.04), 0.0, 1.0);
        
        // 2. Quantize luminance into 3 distinct hard cel-shaded lighting bands
        float cel;
        if (gray < 0.22)      cel = 0.35;
        else if (gray < 0.65) cel = 0.72;
        else                  cel = 1.0;
        
        vec3 shaded = sat_color * cel;
        
        // 3. Add anime screen-tone speedlines/highlight shimmers in bright regions
        float diagonal = sin((pixel.x + pixel.y) * 0.25 - u_time * 5.0) * 0.5 + 0.5;
        if (gray > 0.70) {
            // Overlay a soft pastel sakura pink glow
            vec3 sakura_glow = vec3(1.0, 0.90, 0.95);
            shaded = mix(shaded, sakura_glow, step(0.78, diagonal) * 0.32);
        }
        
        // 4. Draw clean anime outline inking
        float edges8 = edge_detect(screen_uv, texel * 1.8);
        float edge_mask8 = smoothstep(0.12, 0.26, edges8);
        final_color = mix(shaded, vec3(0.04, 0.04, 0.08), edge_mask8 * 0.96);
    }
    else {
        // ==================== MODE 9: SPIDER-VERSE — VINTAGE DARK COMIC INK ====================
        vec3 vc_paper  = vec3(0.91, 0.86, 0.76);  // aged yellowed paper
        vec3 vc_ink    = vec3(0.04, 0.02, 0.04);   // deep print ink black
        vec3 vc_red    = vec3(0.68, 0.05, 0.06);   // dark spider-red
        vec3 vc_dkred  = vec3(0.25, 0.02, 0.03);   // very dark shadow red
        
        // Large halftone dots on 30deg angle (vintage comic printing)
        float vc_ht = halftone(pixel, radians(30.0), 12.0, gray);
        
        // Hard 3-level shadow mapping
        vec3 vc_base;
        if (gray < 0.22) {
            vc_base = vc_ink;
        } else if (gray < 0.50) {
            vc_base = mix(vc_ink, vc_dkred, vc_ht);
        } else if (gray < 0.76) {
            vc_base = mix(vc_dkred, vc_red, vc_ht);
        } else {
            vc_base = mix(vc_red, vc_paper, vc_ht);
        }
        
        // Vertical cross-hatching in deep shadow (classic comic ink)
        float hv = fract(pixel.x * 0.175);
        float hh = fract(pixel.y * 0.175);
        if (gray < 0.32 && (hv < 0.13 || hh < 0.13)) {
            vc_base = vc_ink;
        }
        
        // Extra thick ink outline (comic book panel inking)
        float edges9 = edge_detect(screen_uv, texel * 3.0);
        float edge_mask9 = smoothstep(0.09, 0.22, edges9);
        final_color = mix(vc_base, vc_ink, edge_mask9 * 0.99);
    }
    
    // Add fine paper grain noise
    float grain = (random(screen_uv + vec2(u_time * 0.17, u_time * 0.31)) - 0.5) * 0.05;
    final_color += vec3(grain);
    
    // Vignette overlay
    vec2 qc = TexCoords - 0.5;
    float vig = 1.0 - dot(qc, qc) * 0.5;
    final_color *= vig;
    
    FragColor = vec4(clamp(final_color, 0.0, 1.0), 1.0);
}
