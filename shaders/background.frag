#version 330 core
in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D u_camera_texture;

void main()
{
    FragColor = texture(u_camera_texture, TexCoords);
}
