// Geometry Shader
#version 150
layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;

in  vec4 vColor[];
in  float vArrayID[];

out vec4 gColor;
out float gDist;
out  float gArrayID;

uniform float uLineWidth;
uniform ivec2 uSCSize;
void main()
{

    vec4 n = vec4( (gl_in[1].gl_Position[1]-gl_in[0].gl_Position[1])*uSCSize.y,
                  (-gl_in[1].gl_Position[0]+gl_in[0].gl_Position[0])*uSCSize.x,
		   0, 0);

    float len = sqrt(pow(n.x, 2) + pow(n.y, 2));
    n = n/len*(uLineWidth+0.7);
    n.xy = n.xy/uSCSize.xy;

    vec4 n0 = n*gl_in[0].gl_Position.w;
    vec4 n1 = n*gl_in[1].gl_Position.w;
    
    gColor = vColor[0];
    gArrayID = vArrayID[0];
    int extra_w = 3;
    
    gDist  = -uLineWidth-extra_w;
    gl_Position = gl_in[0].gl_Position + n0;
    EmitVertex();
    
    gl_Position = gl_in[0].gl_Position - n0;
    gDist  = uLineWidth+extra_w;    
    EmitVertex();

    gColor = vColor[1];
    gArrayID = vArrayID[1];
    
    gl_Position = gl_in[1].gl_Position + n1;
    gDist  = -uLineWidth-extra_w;        
    EmitVertex();
    
    gDist  = uLineWidth+extra_w;            
    gl_Position = gl_in[1].gl_Position - n1;

    EmitVertex();

    EndPrimitive();
}
