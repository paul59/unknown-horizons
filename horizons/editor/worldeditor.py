# ###################################################
# Copyright (C) 2012 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

import os
import os.path

from collections import deque

from horizons.constants import GROUND
from horizons.command.unit import RemoveUnit
from horizons.entities import Entities
from horizons.gui.util import load_uh_widget
from horizons.util.dbreader import DbReader
from horizons.util.python.callback import Callback
from horizons.util.shapes import Point, Rect
from horizons.util.uhdbaccessor import read_savegame_template

class WorldEditor(object):
	def __init__(self, world):
		super(WorldEditor, self).__init__()
		self.world = world
		self.session = world.session
		self._remove_unnecessary_objects()
		self._center_view()

		self.brush_size = 1
		self._show_settings()
		self._change_brush_size(1)

		self._create_intermediate_map()

	def _show_settings(self):
		"""Display settings widget to change brush size."""
		self.widget = load_uh_widget('editor_settings.xml')
		for i in range(1, 4):
			b = self.widget.findChild(name='size_%d' % i)
			b.capture(Callback(self._change_brush_size, i))
		self.widget.show()

	def _change_brush_size(self, size):
		"""Change the brush size and update the gui."""
		images = {
		  'box_highlighted': 'content/gui/icons/ship/smallbutton_a.png',
		  'box': 'content/gui/icons/ship/smallbutton.png',
		}

		b = self.widget.findChild(name='size_%d' % self.brush_size)
		b.up_image = images['box']

		self.brush_size = size
		b = self.widget.findChild(name='size_%d' % self.brush_size)
		b.up_image = images['box_highlighted']

	def _remove_unnecessary_objects(self):
		# Delete all ships.
		for ship in (ship for ship in self.world.ships):
			RemoveUnit(ship).execute(self.session)

	def _center_view(self):
		min_x = min(zip(*self.world.full_map.keys())[0])
		max_x = max(zip(*self.world.full_map.keys())[0])
		min_y = min(zip(*self.world.full_map.keys())[1])
		max_y = max(zip(*self.world.full_map.keys())[1])
		self.session.view.center((min_x + max_x) // 2, (min_y + max_y) // 2)

	def _get_double_repr(self, coords):
		if coords not in self.world.full_map:
			return 0

		tile = self.world.full_map[coords]
		if tile.id <= 0:
			return 0 # deep water
		elif tile.id == 1:
			return 1 # shallow water
		elif tile.id == 6:
			return 2 # sand
		elif tile.id == 3:
			return 3 # grass
		else:
			offset = 0 if tile.id == 2 else (1 if tile.id == 5 else 2)
			rot = tile._instance.getRotation() // 90
			if tile._action == 'straight':
				return offset + (1, 0, 0, 1)[rot] # 2 low, 2 high
			elif tile._action == 'curve_in':
				return offset + (1, 1, 0, 1)[rot] # 1 low, 3 high
			else:
				return offset + (1, 0, 0, 0)[rot] # 3 low, 1 high

	def _create_intermediate_map(self):
		self._intermediate_map = {}
		width = self.world.max_x - self.world.min_x + 1
		height = self.world.max_y - self.world.min_y + 1
		for dy in xrange(height + 2):
			orig_y = dy + self.world.min_y - 1
			for dx in xrange(width + 2):
				orig_x = dx + self.world.min_x - 1
				self._intermediate_map[(dx, dy)] = self._get_double_repr((orig_x, orig_y))
		#self._print_intermediate_map()

	def _print_intermediate_map(self):
		width = self.world.max_x - self.world.min_x + 1
		height = self.world.max_y - self.world.min_y + 1
		for dy in xrange(1, 2 * height + 4, 2):
			s = ''
			for dx in xrange(1, 2 * width + 4, 2):
				s += str(self._intermediate_map[(dx // 2, dy // 2)])
			print s
		print

	def get_tile_details(self, coords):
		if coords in self.world.full_map:
			tile = self.world.full_map[coords]
			if tile.id == -1:
				return GROUND.WATER
			else:
				return (tile.id, tile._action, tile._instance.getRotation() + 45)
		else:
			return GROUND.WATER

	def _iter_islands(self):
		ground = {}
		for coords, tile in self.world.full_map.iteritems():
			if tile.id <= 0:
				continue
			ground[coords] = None

		moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

		n = 0
		for coords in sorted(ground.iterkeys()):
			if ground[coords] is not None:
				continue

			coords_list = [coords]
			ground[coords] = n
			queue = deque([coords])
			while queue:
				x, y = queue[0]
				queue.popleft()
				for dx, dy in moves:
					coords2 = (x + dx, y + dy)
					if coords2 in ground and ground[coords2] is None:
						ground[coords2] = n
						queue.append(coords2)
						coords_list.append(coords2)
			n += 1
			yield coords_list

	def _save_islands(self, db, path, prefix):
		for coords_list in self._iter_islands():
			min_x, min_y = 1000000000, 1000000000
			for x, y in coords_list:
				if x < min_x:
					min_x = x
				if y < min_y:
					min_y = y
	
			island_name = '%s_island_%d_%d.sqlite' % (prefix, min_x, min_y)
			island_db_path = os.path.join(path, island_name)
			if os.path.exists(island_db_path):
				os.unlink(island_db_path) # the process relies on having an empty file
			db('INSERT INTO island (x, y, file) VALUES(?, ?, ?)', min_x, min_y, 'content/islands/' + island_name)

			island_db = DbReader(island_db_path)
			island_db('CREATE TABLE ground(x INTEGER NOT NULL, y INTEGER NOT NULL, ground_id INTEGER NOT NULL, action_id TEXT NOT NULL, rotation INTEGER NOT NULL)')
			island_db('CREATE TABLE island_properties(name TEXT PRIMARY KEY NOT NULL, value TEXT NOT NULL)')
			island_db('BEGIN')
			for x, y in coords_list:
				tile = self.world.full_map[(x, y)]
				island_db('INSERT INTO ground VALUES(?, ?, ?, ?, ?)', x - min_x, y - min_y, tile.id, tile._action, tile._instance.getRotation() + 45)
			island_db('COMMIT')
			island_db.close()

	def save_map(self, path, prefix):
		map_file = os.path.join(path, prefix + '.sqlite')
		if os.path.exists(map_file):
			os.unlink(map_file) # the process relies on having an empty file
		db = DbReader(map_file)
		read_savegame_template(db)
		db('BEGIN')
		self._save_islands(db, path, prefix)
		db('COMMIT')
		db.close()

	def _get_intermediate_coords(self, coords):
		return (coords[0] - self.world.min_x, coords[1] - self.world.min_y)

	def _update_intermediate_coords(self, coords, new_type):
		if self._intermediate_map[coords] == new_type:
			return
		self._intermediate_map[coords] = new_type

	def set_tile_from_intermediate(self, x, y):
		if (x, y) not in self._intermediate_map:
			return
		if (x + 1, y + 1) not in self._intermediate_map:
			return

		data = []
		for dy in xrange(2):
			for dx in xrange(2):
				data.append(self._intermediate_map[(x + dx, y + dy)])
		coords = (x + self.world.min_x, y + self.world.min_y)

		mi = min(data)
		for i in xrange(4):
			data[i] -= mi
		if max(data) == 0:
			# the same tile
			if mi == 0:
				self.set_tile(coords, GROUND.WATER)
			elif mi == 1:
				self.set_tile(coords, GROUND.SHALLOW_WATER)
			elif mi == 2:
				self.set_tile(coords, GROUND.SAND)
			elif mi == 3:
				self.set_tile(coords, GROUND.DEFAULT_LAND)
		else:
			assert max(data) == 1, 'This should never happen'
			type = 2 if mi == 0 else (5 if mi == 1 else 4)
			if data == [0, 1, 0, 1]:
				self.set_tile(coords, (type, 'straight', 45))
			elif data == [1, 1, 0, 0]:
				self.set_tile(coords, (type, 'straight', 135))
			elif data == [1, 0, 1, 0]:
				self.set_tile(coords, (type, 'straight', 225))
			elif data == [0, 0, 1, 1]:
				self.set_tile(coords, (type, 'straight', 315))
			elif data == [0, 1, 1, 1]:
				self.set_tile(coords, (type, 'curve_in', 45))
			elif data == [1, 1, 0, 1]:
				self.set_tile(coords, (type, 'curve_in', 135))
			elif data == [1, 1, 1, 0]:
				self.set_tile(coords, (type, 'curve_in', 225))
			elif data == [1, 0, 1, 1]:
				self.set_tile(coords, (type, 'curve_in', 315))
			elif data == [0, 0, 0, 1]:
				self.set_tile(coords, (type, 'curve_out', 45))
			elif data == [0, 1, 0, 0]:
				self.set_tile(coords, (type, 'curve_out', 135))
			elif data == [1, 0, 0, 0]:
				self.set_tile(coords, (type, 'curve_out', 225))
			elif data == [0, 0, 1, 0]:
				self.set_tile(coords, (type, 'curve_out', 315))
			else:
				assert False, 'This should never happen'

	def _fix_intermediate(self, coords_list, new_type):
		changes = True
		while changes:
			changes = False
			for x, y in coords_list:
				top_left = (x, y)
				if top_left not in self._intermediate_map:
					continue
				bottom_right = (x + 1, y + 1)
				if bottom_right not in self._intermediate_map:
					continue
				if self._intermediate_map[top_left] != self._intermediate_map[bottom_right]:
					continue
				bottom_left = (x, y + 1)
				top_right = (x + 1, y)
				if self._intermediate_map[bottom_left] != self._intermediate_map[top_right]:
					continue
				diff = self._intermediate_map[top_left] - self._intermediate_map[top_right]
				if diff == 0:
					continue

				lower_corner = top_right if diff == 1 else top_left
				higher_corner = top_left if diff == 1 else top_right
				mi = self._intermediate_map[lower_corner]
				if new_type <= mi:
					self._set_intermediate_coords(Point(*higher_corner), mi)
				else:
					self._set_intermediate_coords(Point(*lower_corner), mi + 1)
				changes = True

	def set_south_east_corner(self, coords, tile_details):
		x, y = coords
		if not (self.world.min_x <= x < self.world.max_x and self.world.min_y <= y < self.world.max_y):
			return

		dx, dy = self._get_intermediate_coords(coords)
		new_type = tile_details[0] if tile_details[0] != 6 else 2
		if self._intermediate_map[(dx, dy)] == new_type:
			return
		self._set_intermediate_coords(Point(dx, dy), new_type)

	def _get_surrounding_coords(self, current_coords_list):
		all_neighbours = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
		current_coords_set = set(current_coords_list)
		result = set()
		for x, y in current_coords_list:
			for dx, dy in all_neighbours:
				coords2 = (x + dx, y + dy)
				if coords2 in self._intermediate_map and coords2 not in current_coords_set:
					result.add(coords2)
		return sorted(result)

	def _set_intermediate_coords(self, inter_shape, new_type):
		last_coords_list = []
		for coords in inter_shape.tuple_iter():
			if coords not in self._intermediate_map:
				continue
			last_coords_list.append(coords)
			self._update_intermediate_coords(coords, new_type)

		for dist in xrange(3):
			surrounding_coords_list = self._get_surrounding_coords(last_coords_list)
			for coords2 in surrounding_coords_list:
				if coords2 not in self._intermediate_map:
					continue
				cur_type = self._intermediate_map[coords2]
				best_new_type = cur_type
				best_dist = 10
				for new_type2 in xrange(4):
					if best_dist <= abs(new_type2 - cur_type):
						continue
					suitable = True
					for updated_coords in last_coords_list:
						if abs(updated_coords[0] - coords2[0]) > 1 or abs(updated_coords[1] - coords2[1]) > 1:
							continue
						if abs(self._intermediate_map[updated_coords] - new_type2) > 1:
							suitable = False
							break
					if not suitable:
						continue
					best_new_type = new_type2
					best_dist = abs(new_type2 - cur_type)
				self._update_intermediate_coords(coords2, best_new_type)
			last_coords_list.extend(surrounding_coords_list)

		self._fix_intermediate(last_coords_list, new_type)
		#self._print_intermediate_map()

		for coords in last_coords_list:
			self.set_tile_from_intermediate(*coords)

	def set_tile(self, coords, tile_details):
		if coords in self.world.full_map:
			if coords in self.world.full_map:
				old_tile = self.world.full_map[coords]
				if old_tile.id != -1:
					instance = old_tile._instance
					layer = instance.getLocation().getLayer()
					layer.deleteInstance(instance)

			(ground_id, action_id, rotation) = tile_details
			ground = Entities.grounds[ground_id](self.session, *coords)
			ground.act(action_id, rotation)
			self.world.full_map[coords] = ground
			# TODO: update the minimap