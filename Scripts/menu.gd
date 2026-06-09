extends Control
class_name Menu


func _ready():
	RenderingServer.set_default_clear_color(Color.BLACK)


func _on_start_pressed():
	get_tree().change_scene_to_file("res://Scenes/world.tscn")


func _on_help_pressed():
	%Main.visible = false
	%Help.visible = true


func _on_back_pressed():
	%Help.visible = false
	%Main.visible = true


func _on_quit_pressed():
	get_tree().quit()
